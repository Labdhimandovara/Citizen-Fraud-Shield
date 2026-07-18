#!/usr/bin/env python3
import numpy as np
from PIL import Image
import os

def generate_currency_images():
    print("Generating currency training data...")
    
    # Genuine images (50)
    for i in range(50):
        image = np.ones((224, 224, 3))
        for x in range(224):
            for y in range(224):
                progress = y / 224
                image[x, y] = [
                    0.5 + progress * 0.2,
                    0.5 + progress * 0.2,
                    progress * 0.1
                ]
        
        y_coord, x_coord = np.ogrid[-1:1:224*1j, -1:1:224*1j]
        mask = x_coord*x_coord + y_coord*y_coord <= 0.5
        image[mask] = np.minimum(image[mask] + 0.15, 1.0)
        
        thread_x = 56
        image[:, thread_x-2:thread_x+2] = [0.5, 0.5, 0.5]
        
        img_pil = Image.fromarray((image * 255).astype(np.uint8))
        img_pil.save(f"data/currency/genuine/genuine_{i}.png")
        if (i + 1) % 10 == 0:
            print(f"  ✅ Generated {i + 1}/50 genuine images")
    
    print("  ✅ Genuine images done!")
    
    # Counterfeit images (50)
    for i in range(50):
        image = np.random.rand(224, 224, 3)
        from scipy.ndimage import gaussian_filter
        image = gaussian_filter(image, sigma=1.5)
        
        img_pil = Image.fromarray((image * 255).astype(np.uint8))
        img_pil.save(f"data/currency/counterfeit/counterfeit_{i}.png")
        if (i + 1) % 10 == 0:
            print(f"  ✅ Generated {i + 1}/50 counterfeit images")
    
    print("  ✅ Counterfeit images done!")

def generate_call_transcripts():
    print("\nGenerating call transcripts...")
    
    fraud_examples = [
        "This is CBI. We found illegal money laundering on your account. Transfer all funds immediately to a secure government account now or you will be arrested. Do not tell anyone.",
        
        "This is ED - Enforcement Directorate. You are under investigation for cryptocurrency fraud. Transfer funds immediately for verification.",
        
        "This is your bank. Suspicious activity detected. Provide your OTP immediately to verify your identity.",
        
        "You are selected for exclusive investment. 100% profit guaranteed in 30 days risk-free. Send 1 lakh rupees now.",
        
        "ICICI Bank security. Provide CVV and OTP immediately for account verification.",
    ]
    
    for i, call in enumerate(fraud_examples):
        with open(f"data/calls/fraud/fraud_{i}.txt", "w") as f:
            f.write(call)
        print(f"  ✅ Fraud call {i+1}/5")
    
    legitimate_examples = [
        "Hi, customer service here. We have a new plan that might save you money. Are you interested?",
        
        "Hello, this is your insurance company confirming your policy details. Could you verify your address?",
        
        "Hi, delivery service here. Your order will arrive tomorrow between 2-4 PM. Is that okay?",
        
        "Hello, Dr. Singh clinic. Confirming your appointment tomorrow at 3 PM. Please arrive 10 minutes early.",
        
        "Hey, it's your friend. Are you free this weekend? Want to grab dinner?",
    ]
    
    for i, call in enumerate(legitimate_examples):
        with open(f"data/calls/legitimate/legitimate_{i}.txt", "w") as f:
            f.write(call)
        print(f"  ✅ Legitimate call {i+1}/5")

if __name__ == "__main__":
    generate_currency_images()
    generate_call_transcripts()
    print("\n✅ All training data generated!")