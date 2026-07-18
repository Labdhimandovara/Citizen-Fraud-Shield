"""
Citizen Fraud Shield - Final Premium Dashboard v5
Gray/Pink/White color scheme with perfect text visibility
"""

from fastapi import background
from pydantic import color
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import base64
from pathlib import Path
from PIL import Image
from languages_comprehensive import LanguageManager

# ================== PAGE CONFIG ==================

st.set_page_config(
    page_title="Citizen Fraud Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== ELEGANT GRAY/PINK/WHITE PALETTE ==================

PALETTE = {
    # Pinks
    "pink_light": "#F5E6E8",      # Very light pink (backgrounds)
    "pink_accent": "#E8D5D5",     # Soft pink (accents)
    "pink_medium": "#D4A8A8",     # Medium pink (hover states)
    "pink_dark": "#C85A54",       # Dark pink (active states)
    
    # Grays
    "gray_light": "#F8F7F7",      # Nearly white
    "gray_100": "#F0EEEE",        # Light gray
    "gray_200": "#E5E3E3",        # Soft gray
    "gray_300": "#D0CDCD",        # Medium gray
    "gray_500": "#989898",        # Dark gray
    "gray_700": "#4A4A4A",        # Very dark gray
    
    # Accent Colors (with pink/gray harmony)
    "green": "#A8D5BA",           # Soft green (success)
    "orange": "#F4A78B",          # Coral orange (warning)
    "red": "#D9534F",             # Muted red (danger)
    "blue": "#A8C5D6",            # Soft blue (info)
    
    # Text
    "text_primary": "#2C2C2C",    # Almost black
    "text_secondary": "#666666",  # Dark gray
    "text_light": "#FFFFFF",      # Pure white
    "text_muted": "#999999",      # Medium gray
    
    # Backgrounds
    "bg_primary": "#FFFFFF",      # White
    "bg_secondary": "#F8F7F7",    # Off-white
    "bg_tertiary": "#F0EEEE",     # Light gray
}

# ================== CUSTOM CSS - PERFECT CONTRAST ==================

st.markdown(f"""
<style>
    /* Global Styles */
    html, body, [data-testid="stAppViewContainer"] {{
        background: linear-gradient(135deg, {PALETTE['gray_light']} 0%, {PALETTE['pink_light']} 100%);
        color: {PALETTE['text_primary']};
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {PALETTE['pink_accent']} 0%, {PALETTE['gray_100']} 100%);
        box-shadow: 2px 0 15px rgba(0, 0, 0, 0.08);
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        color: {PALETTE['text_primary']} !important;
    }}
    
    [data-testid="stSidebar"] .stText {{
        color: {PALETTE['text_primary']} !important;
    }}
    
    [data-testid="stSidebar"] label {{
        color: {PALETTE['text_primary']} !important;
        font-weight: 600 !important;
    }}
    
    /* Headers */
    h1 {{
        background: linear-gradient(90deg, {PALETTE['pink_medium']} 0%, {PALETTE['gray_500']} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.8rem;
        font-weight: 900;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }}
    
    h2 {{
        color: {PALETTE['pink_medium']};
        font-size: 1.8rem;
        font-weight: 800;
        margin-top: 25px;
        margin-bottom: 15px;
        border-bottom: 3px solid {PALETTE['gray_300']};
        padding-bottom: 10px;
    }}
    
    h3 {{
        color: {PALETTE['text_primary']};
        font-weight: 700;
        font-size: 1.2rem;
    }}
    
    p, span, label {{
        color: {PALETTE['text_primary']} !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        background: linear-gradient(90deg, {PALETTE['pink_accent']} 0%, {PALETTE['pink_medium']} 100%) !important;
        color: {PALETTE['text_light']} !important;
        border-radius: 12px;
        padding: 12px 28px;
        font-size: 1rem;
        font-weight: 700;
        border: none;
        box-shadow: 0 4px 12px rgba(232, 213, 213, 0.4);
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(212, 168, 168, 0.5);
        background: linear-gradient(90deg, {PALETTE['pink_medium']} 0%, {PALETTE['pink_dark']} 100%) !important;
    }}
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: #1D2430 !important;
        color: #F7F8FC !important;
        border: 2px solid {PALETTE['gray_200']} !important;
        border-radius: 10px;
        padding: 12px 14px;
        font-size: 1rem;
    }}
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {PALETTE['pink_medium']} !important;
        box-shadow: 0 0 0 3px rgba(232, 213, 213, 0.2) !important;
        outline: none;
    }}

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {{
        color: rgba(247, 248, 252, 0.65) !important;
    }}
    
    /* Checkboxes & Radio */
    .stCheckbox label,
    .stRadio label {{
        color: {PALETTE['text_primary']} !important;
        font-weight: 600 !important;
    }}
    
    /* Risk Cards */
    .risk-high {{
        background: linear-gradient(135deg, #FFE5E5 0%, #FFD4D4 100%);
        border-left: 5px solid {PALETTE['red']};
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(217, 83, 79, 0.1);
    }}
    
    .risk-high h3 {{
        color: {PALETTE['red']} !important;
    }}
    
    .risk-medium {{
        background: linear-gradient(135deg, #FFF9E5 0%, #FFF3CC 100%);
        border-left: 5px solid {PALETTE['orange']};
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(244, 167, 139, 0.1);
    }}
    
    .risk-medium h3 {{
        color: {PALETTE['orange']} !important;
    }}
    
    .risk-low {{
        background: linear-gradient(135deg, #E8F8F0 0%, #D4F1E5 100%);
        border-left: 5px solid {PALETTE['green']};
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(168, 213, 186, 0.1);
    }}
    
    .risk-low h3 {{
        color: {PALETTE['green']} !important;
    }}
    
    /* Metrics */
    .stMetric {{
        background: {PALETTE['text_light']};
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
        border-top: 4px solid {PALETTE['pink_accent']};
    }}
    
    .stMetric label {{
        color: {PALETTE['text_secondary']} !important;
        font-weight: 600 !important;
    }}
    
    /* Tabs */
    .stTabs {{
        border-bottom: 3px solid {PALETTE['gray_200']};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        color: {PALETTE['text_secondary']} !important;
    }}
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        color: {PALETTE['pink_medium']} !important;
        border-bottom: 3px solid {PALETTE['pink_medium']} !important;
    }}
    
  div[data-testid="stExpander"] {{
    background: #FFFFFF !important;
    border: 1px solid #D6E4F0 !important;
    border-radius: 14px !important;
    box-shadow: 0 3px 10px rgba(0,0,0,.06) !important;
    overflow: hidden;
    margin-top: 15px;
    margin-bottom: 20px;
}}

div[data-testid="stExpander"] details summary {{
    background: #F8FBFF !important;
    border-left: 6px solid #2563EB;
    padding: 16px 18px !important;
    font-size: 1.15rem !important;
    font-weight: 800 !important;
    color: #1E3A8A !important;
    border-radius: 14px;
}}

div[data-testid="stExpander"] details summary:hover {{
    background: #EEF6FF !important;
}}

div[data-testid="stExpander"] details[open] summary {{
    border-bottom: 1px solid #E5E7EB;
}}


    /* Alert Boxes */
    .stInfo {{
        background-color: rgba(168, 197, 214, 0.1);
        border-left: 4px solid {PALETTE['blue']};
        color: {PALETTE['text_primary']};
    }}
    
    .stSuccess {{
        background-color: rgba(168, 213, 186, 0.1);
        border-left: 4px solid {PALETTE['green']};
        color: {PALETTE['text_primary']};
    }}
    
    .stWarning {{
        background-color: rgba(244, 167, 139, 0.1);
        border-left: 4px solid {PALETTE['orange']};
        color: {PALETTE['text_primary']};
    }}
    
    .stError {{
        background-color: rgba(217, 83, 79, 0.1);
        border-left: 4px solid {PALETTE['red']};
        color: {PALETTE['text_primary']};
    }}
    
    /* Chat Messages */
    .stChatMessage {{
        background: transparent;
        border: none;
        padding: 0.15rem 0;
    }}

    /* ===== MINIMAL FINTECH LAYOUT ===== */
    .block-container {{
        max-width: 1240px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        border: 1px solid #E9EDF5 !important;
        border-radius: 20px !important;
        background: #FFFFFF !important;
        box-shadow: 0 12px 28px rgba(22, 36, 62, 0.08) !important;
    }}

    [data-testid="stMetric"] {{
        border: 1px solid #E9EDF5;
        border-top: 3px solid #6C7CF6;
        border-radius: 16px;
        box-shadow: none;
        padding: 1.1rem 1.25rem;
    }}

   /* ==========================================================
   AI ASSISTANT
========================================================== */

.chat-hero {{
    background: linear-gradient(135deg,#0F2747 0%,#1F4D7A 100%);
    border-radius:22px;
    padding:24px 28px;
    margin-bottom:20px;
    box-shadow:0 10px 24px rgba(15,39,71,.18);
}}

.chat-hero h2 {{
    color: white !important;
    font-size:2rem !important;
    font-weight:800 !important;
    margin:0;
}}

.chat-hero p {{
    color:#E2E8F0 !important;
    margin-top:10px;
    font-size:1rem;
    font-weight:500;
}}
.chat-title{{
    color:#FFFFFF !important;
    font-size:2rem !important;
    font-weight:800 !important;
    margin-bottom:10px;
}}
/* Conversation Area */

.chat-window {{
    background:#FFFFFF;
    border:1px solid #E5E7EB;
    border-radius:18px;
    padding:18px;
    margin-top:15px;
    margin-bottom:15px;
    box-shadow:0 4px 12px rgba(0,0,0,.05);
}}

/* Chat Messages */

[data-testid="stChatMessage"] {{
    margin-bottom:14px;
}}

[data-testid="stChatMessageContent"] {{
    border-radius:22px !important;
    padding:14px 18px !important;
    line-height:1.6 !important;
    font-size:15px !important;
    max-width:76%;
}}

/* USER */

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
[data-testid="stChatMessageContent"] {{

    background:#0A84FF !important;
    color:#FFFFFF !important;
    border-bottom-right-radius:8px !important;
}}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
[data-testid="stChatMessageContent"] * {{
    color:#FFFFFF !important;
}}

/* ASSISTANT */

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
[data-testid="stChatMessageContent"] {{

    background:#F3F4F6 !important;
    border:1px solid #E5E7EB !important;
    color:#111827 !important;
    border-bottom-left-radius:8px !important;
}}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
[data-testid="stChatMessageContent"] * {{
    color:#111827 !important;
}}

/* Chat Input */

[data-testid="stChatInput"] {{
    background:transparent !important;
    border:none !important;
    box-shadow:none !important;
}}

[data-testid="stChatInput"] > div {{
    background:transparent !important;
}}

[data-testid="stChatInput"] textarea {{
    background:#FFFFFF !important;
    color:#111827 !important;
    -webkit-text-fill-color:#111827 !important;
    caret-color:#111827 !important;

    border:1px solid #D8E2EE !important;
    border-radius:28px !important;

    padding:14px 18px !important;

    font-size:16px !important;
}}

[data-testid="stChatInput"] textarea::placeholder {{
    color:#9CA3AF !important;
}}

[data-testid="stChatInput"] button {{
    background:#0A84FF !important;
    color:#FFFFFF !important;

    border:none !important;
    border-radius:50% !important;

    width:42px !important;
    height:42px !important;

    box-shadow:none !important;
}}

    /* ===== SELECTBOX / DROPDOWN FIX (was black text on black bg) ===== */
    /* The closed selectbox control */
    [data-baseweb="select"] > div {{
        background-color: {PALETTE['text_light']} !important;
        color: {PALETTE['text_primary']} !important;
        border: 2px solid {PALETTE['gray_200']} !important;
        border-radius: 10px !important;
    }}
    
    [data-baseweb="select"] * {{
        color: {PALETTE['text_primary']} !important;
    }}
    
    /* The dropdown popover panel that opens on click */
    [data-baseweb="popover"] {{
        background-color: {PALETTE['text_light']} !important;
    }}
    
    [data-baseweb="popover"] ul {{
        background-color: {PALETTE['text_light']} !important;
    }}
    
    /* Individual options in the list */
    [role="listbox"] {{
        background-color: {PALETTE['text_light']} !important;
    }}
    
    li[role="option"] {{
        background-color: {PALETTE['text_light']} !important;
        color: {PALETTE['text_primary']} !important;
    }}
    
    li[role="option"]:hover,
    li[aria-selected="true"] {{
        background-color: {PALETTE['pink_light']} !important;
        color: {PALETTE['text_primary']} !important;
    }}
    
    .chart-card-title {{
        font-weight: 700;
        font-size: 1.05rem;
        color: #111111;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    
    /* ===== DETAILED ANALYSIS PANEL ===== */
    .analysis-card {{
        background: {PALETTE['text_light']};
        border: 1px solid {PALETTE['gray_200']};
        border-left: 5px solid {PALETTE['blue']};
        border-radius: 12px;
        padding: 18px 20px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        color: {PALETTE['text_primary']};
    }}

    .analysis-card p,
    .analysis-card li,
    .analysis-card span {{
        color: {PALETTE['text_primary']} !important;
        font-weight: 500;
        line-height: 1.65;
    }}

    .trust-card {{
        background: {PALETTE['text_light']};
        border: 1px solid {PALETTE['gray_200']};
        border-top: 4px solid {PALETTE['blue']};
        border-radius: 14px;
        padding: 16px;
        min-height: 360px;
        min-width: 280px;
        aspect-ratio: 1 / 1;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        color: {PALETTE['text_primary']};
    }}

    .trust-card-title {{
        font-size: 1.08rem;
        font-weight: 700;
        color: #111111;
        margin-bottom: 8px;
    }}

    .metric-pill {{
        background: {PALETTE['text_light']};
        border: 1px solid {PALETTE['gray_200']};
        border-top: 4px solid {PALETTE['blue']};
        border-radius: 18px;
        padding: 16px 18px;
        min-height: 160px;
        min-width: 180px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        color: {PALETTE['text_primary']};
    }}

    .metric-label {{
        font-size: 1rem;
        color: {PALETTE['text_primary']};
        opacity: 0.9;
        margin-bottom: 10px;
    }}

    .metric-value {{
        font-size: 2.6rem;
        font-weight: 700;
        color: {PALETTE['text_primary']};
        line-height: 1.1;
    }}
    
    .recommendation-card {{
        background: {PALETTE['text_light']};
        border: 1px solid {PALETTE['gray_200']};
        border-left: 5px solid {PALETTE['green']};
        border-radius: 12px;
        padding: 18px 20px;
        margin: 10px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        color: {PALETTE['text_primary']};
    }}
    
    .factor-row {{
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px dashed {PALETTE['gray_200']};
        color: {PALETTE['text_primary']};
    }}
    
    .factor-row:last-child {{
        border-bottom: none;
    }}
</style>
""", unsafe_allow_html=True)

# ================== SESSION STATE ==================

if "language" not in st.session_state:
    st.session_state.language = "en"

if "api_status" not in st.session_state:
    st.session_state.api_status = None

if "messages" not in st.session_state:
    st.session_state.messages = []

lang_manager = LanguageManager()
LOGO_PATH = Path(__file__).parent / "assets" / "logo_transparent.png"
LOGO_FALLBACK_PATH = Path(__file__).parent / "assets" / "logo.png"


def _show_logo(max_width: int = 260):
    path = LOGO_PATH if LOGO_PATH.exists() else LOGO_FALLBACK_PATH
    if path.exists():
        try:
            st.image(Image.open(path), width=max_width)
        except Exception:
            st.image(str(path), width=max_width)


def render_app_header():
    logo_path = LOGO_PATH if LOGO_PATH.exists() else LOGO_FALLBACK_PATH
    left, right = st.columns([0.95, 4.05])
    with left:
        if logo_path.exists():
            st.image(Image.open(logo_path), width=101)
    with right:
        st.markdown(
            f"""
            <div style="display:flex; flex-direction:column; gap:6px; padding:2px 0 0 0;">
                <div style="display:flex; align-items:center; gap:14px; flex-wrap:wrap;">
                    <div style="font-size:1.55rem; font-weight:800; color:#0F172A; line-height:1;">Citizen Fraud Shield</div>
                </div>
                <div style="display:flex; flex-direction:column; gap:2px;">
                    <div style="font-size:0.98rem; color:#2563EB; font-weight:600; letter-spacing:0.2px;">Detect • Verify • Protect</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def get_text(key):
    return lang_manager.get_text(key, st.session_state.language)

RESULT_COPY = {
    "en": {"reviewed": "The risk check reviews the transaction amount, transaction frequency, account age, device consistency, location consistency, and merchant category.", "high": "Several transaction signals need attention. Treat this payment as high risk until you verify it independently.", "medium": "Some transaction signals are unusual. Pause and verify the payment before approving it.", "low": "The available transaction signals look broadly normal, but continue standard payment precautions.", "verify": "Before paying, confirm the payee name and UPI ID/account number using a trusted source—not a link or number supplied in the request.", "stop": "Do not complete the payment or share OTP, PIN, CVV, or passwords.", "check": "Check the amount, merchant, payment purpose, recent transaction activity, device, and location against your usual pattern.", "record": "Save the transaction reference and screenshots. If money has been sent, contact your bank immediately and report it to 1930."},
    "hi": {"reviewed": "जोखिम जांच लेनदेन राशि, लेनदेन की संख्या, खाते की आयु, डिवाइस, स्थान और व्यापारी श्रेणी को देखती है।", "high": "कई लेनदेन संकेत चिंताजनक हैं। स्वतंत्र सत्यापन होने तक इसे उच्च जोखिम मानें।", "medium": "कुछ लेनदेन संकेत असामान्य हैं। भुगतान को मंजूरी देने से पहले रुकें और सत्यापित करें।", "low": "उपलब्ध लेनदेन संकेत सामान्य लगते हैं, फिर भी भुगतान संबंधी सावधानियां रखें।", "verify": "भुगतान से पहले विश्वसनीय स्रोत से प्राप्तकर्ता का नाम और UPI ID/खाता नंबर जांचें।", "stop": "भुगतान न करें और OTP, PIN, CVV या पासवर्ड साझा न करें।", "check": "राशि, व्यापारी, भुगतान का कारण, हाल के लेनदेन, डिवाइस और स्थान को अपनी सामान्य गतिविधि से मिलाएं।", "record": "लेनदेन संदर्भ और स्क्रीनशॉट रखें। पैसा भेज दिया है तो तुरंत बैंक से संपर्क करें और 1930 पर रिपोर्ट करें।"},
}

def result_text(key):
    """Return selected-language text, falling back to English when needed."""
    return RESULT_COPY.get(st.session_state.language, RESULT_COPY["en"])[key]

# ================== HELPER FUNCTIONS ==================

def check_api_status():
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def verify_call_or_audio(transcript_or_audio, is_audio=False):
    try:
        endpoint = "/api/verify/call-recording" if is_audio else "/api/verify/call"
        
        if is_audio:
            audio_b64 = base64.b64encode(transcript_or_audio).decode('utf-8')
            response = requests.post(
                f"http://localhost:8000{endpoint}",
                json={"audio_base64": audio_b64, "language": st.session_state.language},
                timeout=10
            )
        else:
            response = requests.post(
                f"http://localhost:8000{endpoint}",
                json={"transcript": transcript_or_audio, "language": st.session_state.language},
                timeout=10
            )
        
        return response.json()
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

def chat_with_ai(message):
    """Chat with AI using Ollama/Gemini/Claude"""
    try:
        response = requests.post(
            "http://localhost:8000/api/chat",
            json={"message": message, "language": st.session_state.language},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("response", "Unable to get response")
    except Exception as e:
        return f"Error: {str(e)}"

def verify_transaction(data):
    try:
        response = requests.post(
            "http://localhost:8000/api/verify/transaction",
            json={**data, "language": st.session_state.language},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return None

def render_chart_card(fig, title="", icon="📊"):
    """Render a chart without repeating the heading above it."""
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_metric_card(label, value, suffix="", danger=False):
    tone = "#2b2b2b" if not danger else PALETTE["red"]
    st.markdown(
        f"""
        <div class="metric-pill">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color:{tone};">{value}{suffix}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def create_risk_gauge(score):
    fig = go.Figure(data=[go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': get_text("trust_score"), 'font': {'color': PALETTE['text_primary']}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': PALETTE['pink_accent']},
            'steps': [
                {'range': [0, 33], 'color': PALETTE['red']},
                {'range': [33, 66], 'color': PALETTE['orange']},
                {'range': [66, 100], 'color': PALETTE['green']}
            ]
        }
    )])
    fig.update_layout(
        height=300,
        font={'color': '#111111', 'size': 12},
        paper_bgcolor=PALETTE['text_light'],
        plot_bgcolor=PALETTE['bg_tertiary'],
        margin=dict(l=12, r=12, t=36, b=12),
        title_text=get_text("trust_score"),
        title_font=dict(color="#111111")
    )
    return fig

def create_risk_distribution():
    data = {
        'Risk': [get_text('high_risk'), get_text('medium_risk'), get_text('low_risk')],
        'Count': [12, 8, 25]
    }
    df = pd.DataFrame(data)
    fig = px.pie(df, names='Risk', values='Count',
                color_discrete_map={
                    get_text('high_risk'): PALETTE['red'],
                    get_text('medium_risk'): PALETTE['orange'],
                    get_text('low_risk'): PALETTE['green']
                })
    fig.update_layout(
        height=350,
        title_text="Risk Distribution",
        title_font=dict(color="#111111"),
        font={'color': '#111111'},
        paper_bgcolor=PALETTE['text_light'],
        plot_bgcolor=PALETTE['bg_tertiary'],
        legend=dict(font=dict(color="#111111"))
    )
    return fig

def create_verification_trend():
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    values = [10, 12, 15, 18, 20, 22, 25, 28, 30, 32, 35, 38, 40, 42, 45,
              47, 48, 50, 52, 53, 55, 57, 58, 60, 62, 63, 65, 67, 68, 70]
    
    df = pd.DataFrame({'Date': dates, 'Count': values})
    fig = px.line(df, x='Date', y='Count',
                 title=get_text('verification_trends'),
                 markers=True, line_shape='spline')
    fig.update_traces(
        line=dict(color=PALETTE['pink_accent'], width=3),
        marker=dict(color=PALETTE['pink_medium'], size=8)
    )
    fig.update_layout(
        height=300,
        title_text=get_text('verification_trends'),
        title_font=dict(color="#111111"),
        font={'color': '#111111'},
        paper_bgcolor=PALETTE['text_light'],
        plot_bgcolor=PALETTE['bg_tertiary'],
        hovermode='x unified',
        xaxis=dict(title=dict(text="Date", font=dict(color="#111111")), tickfont=dict(color="#111111"), color="#111111"),
        yaxis=dict(title=dict(text="Count", font=dict(color="#111111")), tickfont=dict(color="#111111"), color="#111111")
    )
    return fig

def create_scam_types_chart():
    data = {
        'Type': ['Digital\nArrest', 'OTP\nScam', 'Investment', 'Phishing', 'UPI\nFraud'],
        'Count': [15, 12, 10, 8, 5]
    }
    df = pd.DataFrame(data)
    fig = px.bar(df, x='Type', y='Count',
                title='Top Scam Types',
                color='Count',
                color_continuous_scale=[PALETTE['pink_accent'], PALETTE['pink_medium']])
    fig.update_layout(
        height=300,
        title_font=dict(color="#111111"),
        font={'color': '#111111'},
        paper_bgcolor=PALETTE['text_light'],
        plot_bgcolor=PALETTE['bg_tertiary'],
        xaxis=dict(title=dict(text="Type", font=dict(color="#111111")), tickfont=dict(color="#111111"), color="#111111"),
        yaxis=dict(title=dict(text="Count", font=dict(color="#111111")), tickfont=dict(color="#111111"), color="#111111"),
        coloraxis_colorbar=dict(title=dict(text="Count", font=dict(color="#111111")), tickfont=dict(color="#111111"))
    )
    return fig

def build_ai_analysis_points(result):
    """Build a detailed, multi-point AI analysis from whatever the backend returned,
    plus derived insights from trust_score / risk_level / detailed_factors, so the
    section is never just a bare heading even if the API response is thin."""
    risk_level = result.get("risk_level", "UNKNOWN")
    status = result.get("status", "FINAL")
    trust_score = result.get("trust_score", 0)
    confidence = result.get("confidence", 0)
    explanation = (result.get("explanation") or "").strip()
    factors = result.get("detailed_factors", {}) or {}

    points = []

    if st.session_state.language != "en":
        if explanation:
            points.append(explanation)
        points.extend([
            result_text({"HIGH": "high", "MEDIUM": "medium", "LOW": "low"}.get(risk_level, "medium")),
            result_text("reviewed"),
            f"{get_text('trust_score')}: {trust_score}/100 | {get_text('confidence')}: {confidence*100:.0f}%",
        ])
        return points

    if explanation and st.session_state.language == "en":
        points.append(explanation)

    if status == "VERIFY" or trust_score <= 0 or confidence <= 0:
        points.append("The model was unavailable or not confident enough, so the system returned VERIFY instead of guessing a risk level.")
        reason = factors.get("reason")
        if reason:
            points.append(f"Reason: {reason}")
        return points

    risk_copy = {
        "HIGH": "Multiple strong fraud indicators were detected. This case shows patterns "
                "consistent with known scam techniques and should be treated as high risk "
                "until proven otherwise.",
        "MEDIUM": "Some suspicious indicators were found, but they are not conclusive on their "
                  "own. This case warrants a closer look before taking any action.",
        "LOW": "Few or no fraud indicators were detected. The available signals are broadly "
               "consistent with legitimate activity.",
    }
    points.append(risk_copy.get(risk_level, "Risk level could not be conclusively determined from the available data."))

    points.append(
        f"Trust score of {trust_score}/100 with {confidence*100:.0f}% model confidence — "
        f"{'a low score reflects multiple red flags' if trust_score < 40 else 'a mid-range score reflects mixed signals' if trust_score < 70 else 'a high score reflects mostly clean signals'}."
    )

    if factors:
        summary_bits = []
        friendly_keys = {
            "model_status": "Model status",
            "model_name": "Model name",
            "model_version": "Model version",
            "dataset": "Dataset",
            "training_metadata": "Training details",
            "evaluation_metrics": "Evaluation metrics",
        }
        for key in ["model_status", "model_name", "model_version", "dataset"]:
            if key in factors:
                summary_bits.append(f"{friendly_keys[key]}: {_format_detail_value(factors[key])}")
        if "training_metadata" in factors:
            tm = factors["training_metadata"] or {}
            if isinstance(tm, dict):
                summary_bits.append(
                    "Training details: "
                    + ", ".join(
                        [
                            f"version {tm.get('model_version', 'n/a')}",
                            f"dataset {tm.get('dataset_name', 'n/a')}",
                            f"split {tm.get('split', {})}",
                        ]
                    )
                )
        if "evaluation_metrics" in factors:
            em = factors["evaluation_metrics"] or {}
            if isinstance(em, dict):
                primary = em.get("validation", em)
                summary_bits.append(
                    "Evaluation metrics: "
                    + ", ".join(
                        [
                            f"accuracy {primary.get('accuracy', 0):.4f}",
                            f"precision {primary.get('precision', 0):.4f}",
                            f"recall {primary.get('recall', 0):.4f}",
                            f"f1 {primary.get('f1', 0):.4f}",
                            f"roc auc {primary.get('roc_auc', 0):.4f}",
                        ]
                    )
                )
        if summary_bits:
            points.append("Key factors reviewed — " + "; ".join(summary_bits))

    return points


def build_recommendation_points(result):
    """Build a step-by-step recommendation list based on risk level and action,
    falling back to sensible defaults when the backend doesn't supply one."""
    risk_level = result.get("risk_level", "UNKNOWN")
    recommendation = (result.get("recommendation") or "").strip()
    action = result.get("action", "")

    steps = []
    if st.session_state.language != "en":
        if recommendation:
            steps.append(recommendation)
        if risk_level == "HIGH":
            return steps + [result_text("stop"), result_text("verify"), result_text("record")]
        if risk_level == "MEDIUM":
            return steps + [result_text("verify"), result_text("check"), result_text("record")]
        return steps + [result_text("check"), result_text("verify")]

    if recommendation:
        steps.append(recommendation)

    if risk_level == "HIGH":
        steps += [
            "🚫 Do not share OTP, PIN, password, or Aadhaar details with this caller/sender.",
            "☎️ Do not proceed with any payment or transaction until verified independently.",
            "📞 Verify independently by calling the organization's official number (not one given by the caller).",
            "🛑 Report immediately to NCRP at 1930 or cybercrime.gov.in.",
            "👪 Warn family members who may be targeted by a similar approach.",
        ]
    elif risk_level == "MEDIUM":
        steps += [
            "⏸️ Pause before acting — take time to verify the request through an official channel.",
            "🔍 Cross-check details (sender ID, account name, transaction amount) before proceeding.",
            "📵 Avoid clicking links or sharing codes until you've confirmed legitimacy.",
            "📋 Keep a record (screenshot/call log) in case you need to report it later.",
        ]
    else:
        steps += [
            "✅ No immediate action required — signals are consistent with legitimate activity.",
            "🔁 Continue standard precautions: never share OTP/PIN even for verified contacts.",
            "🧾 Keep monitoring your account statements for anything unusual.",
        ]

    if action and action not in ("UNKNOWN",):
        steps.append(f"Recommended system action: **{action}**")

    return steps


def build_transaction_evidence(data, result):
    """Explain transaction risk using observable payment signals, not vague AI claims."""
    observations = []
    cautions = []
    amount = data.get("amount", 0)
    account_age = data.get("account_age_days", 0)
    transactions = data.get("transactions_24h", 0)

    if amount >= 50000:
        cautions.append(f"High value: ₹{amount:,.0f}. Confirm the payee and purpose before authorising a large payment.")
    else:
        observations.append(f"Amount: ₹{amount:,.0f} is not unusually high based on the entered threshold.")
    if account_age < 30:
        cautions.append(f"New account signal: the account is only {account_age} days old; newly created accounts need extra verification.")
    else:
        observations.append(f"Account age: {account_age} days, so this is not a newly created account signal.")
    if transactions >= 5:
        cautions.append(f"High activity: {transactions} transactions in 24 hours can indicate unusual payment velocity.")
    else:
        observations.append(f"Transaction frequency: {transactions} in 24 hours is within the normal range entered.")
    if data.get("device_mismatch"):
        cautions.append("Device mismatch: the payment is from a new or unrecognised device.")
    else:
        observations.append("Device: no new-device mismatch was reported.")
    if data.get("geographic_mismatch"):
        cautions.append("Location mismatch: the payment location differs from the usual location.")
    else:
        observations.append("Location: no unusual location was reported.")

    observations.append(f"Merchant category: {data.get('merchant_category', 'unknown').replace('_', ' ')}. Category alone does not prove fraud.")
    if result.get("risk_level") == "HIGH" and not cautions:
        cautions.append("The model reported additional risk signals. Verify the payee identity and payment request independently.")
    return cautions, observations


def display_transaction_reasoning(data, result):
    cautions, observations = build_transaction_evidence(data, result)
    st.markdown("### Why this transaction was assessed this way")
    st.caption("This assessment checks behaviour signals; it cannot confirm that a payee, link, or caller is genuine on its own.")
    left, right = st.columns(2)
    with left:
        st.markdown("**Risk signals found**")
        if cautions:
            for item in cautions:
                st.warning(item)
        else:
            st.success("No high-risk behaviour signals were found in the details entered.")
    with right:
        st.markdown("**Signals that look normal**")
        for item in observations:
            st.info(item)


def display_recommendations(result):
    """Keep recommended actions immediately after the evidence section."""
    st.markdown(f"### 📋 {get_text('recommendation')}")
    rec_points = build_recommendation_points(result)
    rec_html = "".join(f"<p style='margin:6px 0;'>{p}</p>" for p in rec_points)
    st.markdown(f'<div class="recommendation-card">{rec_html}</div>', unsafe_allow_html=True)


def _format_detail_value(value):
    if isinstance(value, dict):
        return ", ".join(f"{k}: {v}" for k, v in list(value.items())[:4])
    if isinstance(value, list):
        return ", ".join(map(str, value[:6]))
    return str(value)


def _render_detail_table(rows):
    if not rows:
        return
    frame = pd.DataFrame(rows, columns=["Field", "Value"])
    st.dataframe(
        frame,
        use_container_width=True,
        hide_index=True,
    )


def display_result_modern(result, show_recommendations=True):
    if not result:
        return
    
    risk_level = result.get("risk_level", "UNKNOWN")
    status = result.get("status", "FINAL")
    trust_score = result.get("trust_score", 0)
    fraud_probability = result.get("fraud_probability", 0)
    explanation = result.get("explanation", "")
    recommendation = result.get("recommendation", "")
    confidence = result.get("confidence", 0)
    action = result.get("action", "UNKNOWN")
    reason = (result.get("detailed_factors", {}) or {}).get("reason") or result.get("explanation", "")
    has_assessment = confidence > 0 and status != "VERIFY"
    
    # Risk banner
    if risk_level == "HIGH":
        st.markdown(f'<div class="risk-high"><h3>🔴 {get_text("high_risk")}</h3>', unsafe_allow_html=True)
    elif risk_level == "MEDIUM":
        st.markdown(f'<div class="risk-medium"><h3>🟡 {get_text("medium_risk")}</h3>', unsafe_allow_html=True)
    elif risk_level == "LOW":
        st.markdown(f'<div class="risk-low"><h3>🟢 {get_text("low_risk")}</h3>', unsafe_allow_html=True)
    else:
        if status == "VERIFY":
            st.info(f"⚠️ VERIFY: {reason or 'Model unavailable or confidence below threshold.'}")
        else:
            st.warning("⚠️ Assessment incomplete — the risk engine did not return a usable decision. Please run the check again.")
    
    # Metrics
    col1, col2, col3, col4 = st.columns([1.12, 1, 1, 1])
    
    with col1:
        with st.container():
            if has_assessment:
                st.plotly_chart(
                    create_risk_gauge(trust_score),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )
            else:
                st.markdown(
                    '<div style="display:flex; align-items:center; justify-content:center; min-height:250px; color:#111111; font-weight:700;">Not available</div>',
                    unsafe_allow_html=True,
                )
    
    with col2:
        render_metric_card(get_text("confidence"), f"{confidence*100:.0f}" if has_assessment else "Not available", suffix="%" if has_assessment else "")
    
    with col3:
        scam_prob = fraud_probability * 100
        render_metric_card(get_text("scam_probability"), f"{scam_prob:.0f}" if has_assessment else "Not available", suffix="%" if has_assessment else "", danger=has_assessment and scam_prob >= 70)
    
    with col4:
        render_metric_card(get_text("action"), action if has_assessment else "Review required")

    st.markdown("---")
    
    # ---- Detailed AI Analysis ----
    st.markdown(f"### 🧠 {get_text('ai_analysis')}")
    analysis_points = build_ai_analysis_points(result)
    analysis_html = "".join(f"<p style='margin:6px 0;'>• {p}</p>" for p in analysis_points)
    st.markdown(f'<div class="analysis-card">{analysis_html}</div>', unsafe_allow_html=True)
    
    if show_recommendations:
        display_recommendations(result)
    with st.expander(f"📊 {get_text('detailed_analysis')}", expanded=False):
        st.markdown(f"### {get_text('factors')}")
        factors = result.get("detailed_factors", {})
        dev_rows = []
        if result.get("model_version"):
            dev_rows.append(["Model version", result["model_version"]])
        if result.get("detailed_factors", {}).get("dataset"):
            dev_rows.append(["Dataset", result["detailed_factors"]["dataset"]])
        if result.get("evaluation_metrics"):
            metrics = result["evaluation_metrics"]
            primary = metrics.get("validation", metrics)
            dev_rows.extend([
                ["Accuracy", f"{primary.get('accuracy', 0):.4f}"],
                ["Precision", f"{primary.get('precision', 0):.4f}"],
                ["Recall", f"{primary.get('recall', 0):.4f}"],
                ["F1", f"{primary.get('f1', 0):.4f}"],
                ["ROC-AUC", f"{primary.get('roc_auc', 0):.4f}"],
            ])
        if dev_rows:
            _render_detail_table(dev_rows)
        if factors:
            st.markdown("### Fraud Indicators")
            factor_rows = [
                (k.replace("_", " ").title(), _format_detail_value(v))
                for k, v in factors.items()
            ]
            _render_detail_table(factor_rows)
        else:
            st.caption(result_text("reviewed"))

        st.markdown("### Top Scam Types Nationally")
        render_chart_card(create_scam_types_chart(), "Top Scam Types Nationally", "📈")

# ================== SIDEBAR ==================

with st.sidebar:
    st.markdown(f"# 🛡️ {get_text('app_title')}")
    st.markdown(f"*{get_text('tagline')}*")
    
    st.divider()
    
    st.subheader(f"🌐 {get_text('language_select')}")
    languages = lang_manager.get_all_languages()
    lang_options = {code: f"{lang_manager.get_language_flag(code)} {name}"
                   for code, name in languages.items()}
    
    selected_lang = st.selectbox(
        "Language:",
        options=list(lang_options.keys()),
        format_func=lambda x: lang_options[x],
        index=list(lang_options.keys()).index(st.session_state.language),
        key="lang_select"
    )
    
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()
    
    st.divider()
    
    api_status = check_api_status()
    if api_status:
        st.success(f"✅ {get_text('api_connected')}")
    else:
        st.error("❌ API Offline")
    
    st.divider()
    
    page = st.radio(
        "Navigate:",
        ["📊 Dashboard", "📱 Verify Call/Audio", "💰 Verify Transaction",
         "💵 Verify Currency", "🤖 AI Assistant", "ℹ️ About"],
        label_visibility="collapsed"
    )

# ================== PAGES ==================

if page == "📊 Dashboard":
    render_app_header()
    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    if not api_status:
        st.error("⚠️ API Offline")
    else:
        try:
            stats = requests.get("http://localhost:8000/api/stats", timeout=4).json().get("statistics", {})
        except Exception:
            stats = {}
        total_alerts = stats.get("total_alerts", 0)
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("🔴 High Risk", str(stats.get("high_risk", 0)))
        col2.metric("🟡 Medium Risk", str(stats.get("medium_risk", 0)))
        col3.metric("🟢 Low Risk", str(stats.get("low_risk", 0)))
        col4.metric("📊 Total", str(total_alerts))
        col5.metric("📈 Model Ready", "Yes" if any(stats.values()) else "No data")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            render_chart_card(create_risk_distribution(), "Risk Distribution", "🥧")
        with col2:
            render_chart_card(create_verification_trend(), get_text("verification_trends"), "📈")
        
        st.divider()
        render_chart_card(create_scam_types_chart(), "Top Scam Types", "📊")

elif page == "📱 Verify Call/Audio":
    st.title(f"📞 {get_text('verify_call')}")
    st.markdown("*Analyze transcript or upload audio*")
    
    if not api_status:
        st.error("⚠️ API Offline")
    else:
        tab1, tab2 = st.tabs(["📝 Transcript", "🎙️ Audio"])
        
        with tab1:
            transcript = st.text_area(
                get_text("paste_transcript"),
                placeholder="Example: Hello, this is CBI...",
                height=200
            )
            
            if st.button("🔍 Analyze", use_container_width=True, key="analyze_text"):
                if transcript.strip():
                    with st.spinner("Analyzing..."):
                        result = verify_call_or_audio(transcript)
                        if result:
                            st.session_state.last_result = result
                            st.rerun()
                else:
                    st.warning("Please enter transcript")
        
        with tab2:
            st.info("📁 MP3, WAV, M4A, OGG")
            uploaded_file = st.file_uploader("Upload audio:", type=["mp3", "wav", "m4a", "ogg"])
            
            if uploaded_file and st.button("🔍 Analyze", use_container_width=True, key="analyze_audio"):
                with st.spinner("Analyzing..."):
                    result = verify_call_or_audio(uploaded_file.read(), is_audio=True)
                    if result:
                        st.session_state.last_result = result
                        st.rerun()
        
        if "last_result" in st.session_state:
            st.divider()
            display_result_modern(st.session_state.last_result)

elif page == "💰 Verify Transaction":
    st.title(f"💰 {get_text('verify_transaction')}")
    
    if not api_status:
        st.error("⚠️ API Offline")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            amount = st.number_input("Amount (₹)", min_value=0, step=1000, value=50000)
            account_age = st.number_input("Account Age (days)", min_value=0, value=30)
            avg_amount = st.number_input("Usual transaction amount (₹)", min_value=0, step=500, value=5000)
        
        with col2:
            merchant = st.selectbox("Merchant category", ["online_shopping", "food_delivery", "travel", "utilities", "bank_transfer", "investment", "other"])
            txns_24h = st.number_input("Transactions (24h)", min_value=0, value=2)
            payment_channel = st.selectbox("Payment channel", ["UPI", "bank_transfer", "card", "wallet", "cash"])
            purpose = st.selectbox("Payment purpose", ["purchase", "bill", "friend_or_family", "investment", "refund", "other"])
        
        with col3:
            device_mismatch = st.checkbox("New Device?")
            geo_mismatch = st.checkbox("Different Location?")
            beneficiary_new = st.checkbox("New beneficiary / payee?")
            beneficiary_verified = st.checkbox("Payee details verified independently?")
            unknown_requester = st.checkbox("Payment requested by an unknown person?")
            otp_or_pin_requested = st.checkbox("Did anyone ask for OTP, PIN, or CVV?")
            link_or_qr_received = st.checkbox("Was a payment link or QR sent to you?")

        st.caption("Risk signals combine payment behaviour with payee and social-engineering checks. A low score is not proof that a payee is genuine.")
        
        if st.button("🔍 Analyze", use_container_width=True):
            with st.spinner("Analyzing..."):
                data = {
                    "amount": amount,
                    "merchant_category": merchant,
                    "account_age_days": account_age,
                    "transactions_24h": txns_24h,
                    "avg_transaction_amount": avg_amount,
                    "device_mismatch": device_mismatch,
                    "geographic_mismatch": geo_mismatch,
                    "beneficiary_new": beneficiary_new,
                    "beneficiary_verified": beneficiary_verified,
                    "payment_channel": payment_channel,
                    "payment_purpose": purpose,
                    "unknown_requester": unknown_requester,
                    "otp_or_pin_requested": otp_or_pin_requested,
                    "link_or_qr_received": link_or_qr_received,
                }
                result = verify_transaction(data)
                if result:
                    st.session_state.last_result = result
                    st.session_state.last_transaction_data = data
                    st.session_state.last_result_type = "transaction"
                    st.rerun()
        
        if st.session_state.get("last_result_type") == "transaction":
            st.divider()
            display_result_modern(st.session_state.last_result, show_recommendations=False)
            display_transaction_reasoning(st.session_state.last_transaction_data, st.session_state.last_result)
            display_recommendations(st.session_state.last_result)

elif page == "💵 Verify Currency":
    st.title(f"💵 {get_text('verify_currency')}")
    
    denomination = st.selectbox("Denomination", ["500", "2000", "100", "200"])
    uploaded_file = st.file_uploader("Upload image:", type=["jpg", "jpeg", "png"])
    
    if uploaded_file and st.button("🔍 Analyze", use_container_width=True):
        st.image(uploaded_file, use_column_width=True)
        try:
            response = requests.post(
                "http://localhost:8000/api/verify/currency",
                data={"denomination": denomination, "language": st.session_state.language},
                files={"image_file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                timeout=20,
            )
            response.raise_for_status()
            st.markdown("---")
            display_result_modern(response.json())
        except requests.RequestException as exc:
            st.error(f"Currency verification failed: {exc}")

elif page == "🤖 AI Assistant":
    st.markdown(f"""
<div class="chat-hero">
    <div class="chat-title">
        🤖 {get_text('ai_assistant')}
    </div>

""", unsafe_allow_html=True)
    if not api_status:
        st.warning("⚠️ AI Assistant is temporarily unavailable. Start the API service to chat.")
    else:
        st.markdown(
            "<p style='color:#ffffff; margin:0 0 0.75rem 0; font-weight:500;'>Messages are for fraud-prevention guidance. Never share OTPs, PINs, or passwords.</p>",
            unsafe_allow_html=True,
        )

        # This project uses an older Streamlit release, which supports only a
        # parameterless container. The surrounding chat styles still apply.
        conversation = st.container()
        with conversation:
            if not st.session_state.messages:
                st.info("👋 Hello! Ask me to review a suspicious call, payment request, UPI message, or link.")
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_input = st.chat_input(get_text("ask_anything"))
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner(get_text("thinking")):
                response = chat_with_ai(user_input)
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

elif page == "ℹ️ About":
    st.title(f"ℹ️ About Citizen Fraud Shield")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Mission
        
        Protect every Indian citizen from digital fraud.
        
        ### ✨ Features
        - AI-Powered Detection
        - Call & Audio Analysis
        - Transaction Fraud Detection
        - Currency Verification
        - 12-Language Support
        """)
    
    with col2:
        st.markdown("""
        ### 🔐 Security
        
        - No PII Storage
        - End-to-End Encrypted
        - GDPR Compliant
        - Open Source
        - Real-Time Detection
        """)

st.markdown("---")
st.markdown(f"""
<div style='text-align: center;'>
    <p style='color: {PALETTE["text_secondary"]};'>
        🛡️ Citizen Fraud Shield v5.0 | AI That Protects
    </p>
    <p style='color: {PALETTE["text_muted"]}; font-size: 0.9rem;'>
        Protecting Indian citizens from digital fraud
    </p>
</div>
""", unsafe_allow_html=True)
