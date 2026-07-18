#!/usr/bin/env python3
"""
Citizen Fraud Shield - ML Model Setup & Training Script
Downloads pre-trained models or trains new ones from datasets
"""

import os
import sys
import json
import argparse
from pathlib import Path
import numpy as np

# ================== CONFIGURATION ==================

MODEL_DIRECTORY = Path("models")
DATA_DIRECTORY = Path("data")
LOG_DIRECTORY = Path("logs")

# Model URLs (example - replace with actual URLs)
MODEL_URLS = {
    "currency_cnn.h5": "https://example.com/models/currency_cnn.h5",
    "call_fraud_model.pkl": "https://example.com/models/call_fraud_model.pkl",
}

# ================== SETUP ==================

def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directories...")
    
    for directory in [MODEL_DIRECTORY, DATA_DIRECTORY, LOG_DIRECTORY]:
        directory.mkdir(exist_ok=True)
        print(f"  ✅ Created: {directory}")
    
    # Create subdirectories
    (DATA_DIRECTORY / "currency" / "genuine").mkdir(parents=True, exist_ok=True)
    (DATA_DIRECTORY / "currency" / "counterfeit").mkdir(parents=True, exist_ok=True)
    (DATA_DIRECTORY / "calls" / "fraud").mkdir(parents=True, exist_ok=True)
    (DATA_DIRECTORY / "calls" / "legitimate").mkdir(parents=True, exist_ok=True)
    
    print("  ✅ Directory structure complete")


def create_synthetic_currency_dataset():
    """Generate synthetic currency images for training"""
    print("\n🎨 Generating synthetic currency dataset...")
    
    try:
        from currency_cnn_model import CurrencyDataGenerator
        from PIL import Image
        
        # Create synthetic data
        print("  Generating genuine currency images...")
        for i in range(100):
            image = CurrencyDataGenerator.generate_genuine_currency_image("500")
            # Convert to PIL Image and save
            img_pil = Image.fromarray((image * 255).astype(np.uint8))
            img_pil.save(f"data/currency/genuine/genuine_500_{i}.png")
            if (i + 1) % 25 == 0:
                print(f"    ✅ Generated {i + 1}/100 genuine images")
        
        print("  Generating counterfeit currency images...")
        for i in range(100):
            image = CurrencyDataGenerator.generate_counterfeit_currency_image("500")
            img_pil = Image.fromarray((image * 255).astype(np.uint8))
            img_pil.save(f"data/currency/counterfeit/counterfeit_500_{i}.png")
            if (i + 1) % 25 == 0:
                print(f"    ✅ Generated {i + 1}/100 counterfeit images")
        
        print("  ✅ Synthetic currency dataset created (200 images)")
        
    except Exception as e:
        print(f"  ⚠️ Error generating synthetic currency data: {e}")


def create_synthetic_call_dataset():
    """Generate synthetic call transcripts for training"""
    print("\n📞 Generating synthetic call dataset...")
    
    try:
        from call_fraud_ml_model import CallFraudDataGenerator
        
        fraud_calls = CallFraudDataGenerator.generate_fraud_transcripts()
        legitimate_calls = CallFraudDataGenerator.generate_legitimate_transcripts()
        
        # Save fraud calls
        for i, call in enumerate(fraud_calls):
            with open(f"data/calls/fraud/fraud_{i}.txt", "w") as f:
                f.write(call)
        
        # Save legitimate calls
        for i, call in enumerate(legitimate_calls):
            with open(f"data/calls/legitimate/legitimate_{i}.txt", "w") as f:
                f.write(call)
        
        print(f"  ✅ Created {len(fraud_calls)} fraud call transcripts")
        print(f"  ✅ Created {len(legitimate_calls)} legitimate call transcripts")
        
    except Exception as e:
        print(f"  ⚠️ Error generating synthetic call data: {e}")


def train_currency_model():
    """Train CNN model for currency authentication"""
    print("\n🧠 Training Currency CNN Model...")
    
    try:
        from currency_cnn_model import CurrencyAuthenticationCNN
        from PIL import Image
        import numpy as np
        
        # Load training data
        genuine_dir = DATA_DIRECTORY / "currency" / "genuine"
        counterfeit_dir = DATA_DIRECTORY / "currency" / "counterfeit"
        
        if not genuine_dir.exists() or not counterfeit_dir.exists():
            print("  ⚠️ Dataset not found. Run 'python setup_ml_models.py --create-synthetic' first")
            return False
        
        print("  Loading genuine currency images...")
        genuine_images = []
        for img_path in sorted(genuine_dir.glob("*.png"))[:50]:  # Limit for demo
            img = Image.open(img_path).convert('RGB')
            img = img.resize((224, 224))
            genuine_images.append(np.array(img) / 255.0)
        
        print(f"    ✅ Loaded {len(genuine_images)} genuine images")
        
        print("  Loading counterfeit currency images...")
        counterfeit_images = []
        for img_path in sorted(counterfeit_dir.glob("*.png"))[:50]:  # Limit for demo
            img = Image.open(img_path).convert('RGB')
            img = img.resize((224, 224))
            counterfeit_images.append(np.array(img) / 255.0)
        
        print(f"    ✅ Loaded {len(counterfeit_images)} counterfeit images")
        
        if len(genuine_images) == 0 or len(counterfeit_images) == 0:
            print("  ⚠️ No training images found")
            return False
        
        # Train model
        print("  Training model (this may take 5-10 minutes on CPU)...")
        model = CurrencyAuthenticationCNN()
        
        genuine_array = np.array(genuine_images)
        counterfeit_array = np.array(counterfeit_images)
        
        model.train(genuine_array, counterfeit_array, epochs=5, batch_size=16)
        
        print("  ✅ Currency CNN model trained successfully")
        print(f"  📁 Model saved to: {model.model_path}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error training currency model: {e}")
        return False


def train_call_fraud_model():
    """Train ML model for call fraud detection"""
    print("\n🧠 Training Call Fraud ML Model...")
    
    try:
        from call_fraud_ml_model import CallFraudDetectorML
        
        # Load training data
        fraud_dir = DATA_DIRECTORY / "calls" / "fraud"
        legitimate_dir = DATA_DIRECTORY / "calls" / "legitimate"
        
        if not fraud_dir.exists() or not legitimate_dir.exists():
            print("  ⚠️ Dataset not found. Run 'python setup_ml_models.py --create-synthetic' first")
            return False
        
        print("  Loading fraud call transcripts...")
        fraud_transcripts = []
        for call_path in fraud_dir.glob("*.txt"):
            with open(call_path) as f:
                fraud_transcripts.append(f.read())
        
        print(f"    ✅ Loaded {len(fraud_transcripts)} fraud transcripts")
        
        print("  Loading legitimate call transcripts...")
        legitimate_transcripts = []
        for call_path in legitimate_dir.glob("*.txt"):
            with open(call_path) as f:
                legitimate_transcripts.append(f.read())
        
        print(f"    ✅ Loaded {len(legitimate_transcripts)} legitimate transcripts")
        
        if len(fraud_transcripts) == 0 or len(legitimate_transcripts) == 0:
            print("  ⚠️ No training transcripts found")
            return False
        
        # Train model
        print("  Training model (this may take 1-2 minutes)...")
        model = CallFraudDetectorML()
        model.train(legitimate_transcripts, fraud_transcripts)
        
        print("  ✅ Call Fraud ML model trained successfully")
        print(f"  📁 Model saved to: {model.model_path}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error training call model: {e}")
        return False


def download_pretrained_models():
    """Download pre-trained models (if available)"""
    print("\n📥 Downloading pre-trained models...")
    
    try:
        import urllib.request
        
        for model_name, url in MODEL_URLS.items():
            print(f"  Downloading {model_name}...")
            
            model_path = MODEL_DIRECTORY / model_name
            
            # Note: This is a placeholder. In production, implement actual download
            print(f"    ⚠️ Download URL not configured yet")
            print(f"    💡 To use pre-trained models, configure URLs in setup_ml_models.py")
        
        print("  💡 Alternatively, train models using: --train-all")
        
    except Exception as e:
        print(f"  ⚠️ Error downloading models: {e}")


def verify_setup():
    """Verify that all components are properly set up"""
    print("\n✅ Verifying setup...")
    
    checks = {
        "Models directory": MODEL_DIRECTORY.exists(),
        "Data directory": DATA_DIRECTORY.exists(),
        "Logs directory": LOG_DIRECTORY.exists(),
    }
    
    # Check if models exist
    try:
        from currency_cnn_model import HybridCurrencyAuthenticator
        checks["Currency CNN importable"] = True
    except:
        checks["Currency CNN importable"] = False
    
    try:
        from call_fraud_ml_model import HybridCallFraudDetector
        checks["Call Fraud ML importable"] = True
    except:
        checks["Call Fraud ML importable"] = False
    
    # Check TensorFlow
    try:
        import tensorflow as tf
        checks[f"TensorFlow ({tf.__version__})"] = True
    except:
        checks["TensorFlow"] = False
    
    # Check scikit-learn
    try:
        import sklearn
        checks[f"scikit-learn ({sklearn.__version__})"] = True
    except:
        checks["scikit-learn"] = False
    
    # Print results
    print("\n  Component Status:")
    all_passed = True
    for component, status in checks.items():
        status_icon = "✅" if status else "❌"
        print(f"    {status_icon} {component}")
        if not status:
            all_passed = False
    
    if all_passed:
        print("\n  ✅ All components verified successfully!")
    else:
        print("\n  ⚠️ Some components are missing. Run:")
        print("     pip install -r requirements_ml.txt")
    
    return all_passed


def create_config():
    """Create configuration file"""
    print("\n⚙️ Creating configuration...")
    
    config = {
        "models": {
            "currency": {
                "path": "models/currency_cnn.h5",
                "enabled": True,
                "confidence_threshold": 0.60,
                "model_type": "CNN-MobileNetV2"
            },
            "call_fraud": {
                "path": "models/call_fraud_model.pkl",
                "enabled": True,
                "confidence_threshold": 0.65,
                "model_type": "GradientBoosting"
            },
            "transaction": {
                "path": "models/transaction_rules.json",
                "enabled": True,
                "confidence_threshold": 0.70,
                "model_type": "RuleBasedML"
            }
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "debug": False
        },
        "database": {
            "path": "fraud_alerts.db"
        },
        "logging": {
            "level": "INFO",
            "path": "logs/fraud_shield.log"
        }
    }
    
    config_path = Path("config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"  ✅ Configuration created: {config_path}")


# ================== MAIN ==================

def main():
    parser = argparse.ArgumentParser(
        description="Citizen Fraud Shield ML Model Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete setup with everything
  python setup_ml_models.py --setup-all
  
  # Just create directories
  python setup_ml_models.py --create-dirs
  
  # Generate synthetic data
  python setup_ml_models.py --create-synthetic
  
  # Train all models
  python setup_ml_models.py --train-all
  
  # Verify installation
  python setup_ml_models.py --verify
        """
    )
    
    parser.add_argument("--setup-all", action="store_true",
                       help="Complete setup: dirs + synthetic data + train models")
    parser.add_argument("--create-dirs", action="store_true",
                       help="Create necessary directories")
    parser.add_argument("--create-synthetic", action="store_true",
                       help="Generate synthetic training data")
    parser.add_argument("--download-models", action="store_true",
                       help="Download pre-trained models")
    parser.add_argument("--train-all", action="store_true",
                       help="Train all models from data")
    parser.add_argument("--train-currency", action="store_true",
                       help="Train only currency CNN model")
    parser.add_argument("--train-calls", action="store_true",
                       help="Train only call fraud ML model")
    parser.add_argument("--verify", action="store_true",
                       help="Verify installation")
    parser.add_argument("--config", action="store_true",
                       help="Create configuration file")
    
    args = parser.parse_args()
    
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║   Citizen Fraud Shield - ML Model Setup                ║
    ║   🛡️  Setting up ML-powered fraud detection            ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    # No arguments - show help
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    try:
        if args.setup_all:
            print("\n🚀 Running complete setup...\n")
            setup_directories()
            create_synthetic_currency_dataset()
            create_synthetic_call_dataset()
            train_currency_model()
            train_call_fraud_model()
            create_config()
            verify_setup()
        
        else:
            if args.create_dirs:
                setup_directories()
            
            if args.create_synthetic:
                create_synthetic_currency_dataset()
                create_synthetic_call_dataset()
            
            if args.download_models:
                download_pretrained_models()
            
            if args.train_all:
                train_currency_model()
                train_call_fraud_model()
            elif args.train_currency:
                train_currency_model()
            elif args.train_calls:
                train_call_fraud_model()
            
            if args.verify:
                verify_setup()
            
            if args.config:
                create_config()
        
        print("\n" + "="*60)
        print("✅ Setup completed successfully!")
        print("="*60)
        print("\n📖 Next steps:")
        print("  1. Start API:        python main_ml_integrated.py")
        print("  2. Start Dashboard:  streamlit run dashboard_ml_enhanced.py")
        print("  3. Test endpoints:   curl http://localhost:8000/docs")
        print()
        
    except KeyboardInterrupt:
        print("\n⚠️ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()