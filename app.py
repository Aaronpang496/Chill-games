import streamlit as st
import streamlit.components.v1 as components
import random, json, os, math, struct, io, base64

st.set_page_config(
    page_title="Chill Arcade",
    page_icon="🎮",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ============================================================
# 🌌 GLOBAL DARK THEME — kills the white Streamlit background
# ============================================================
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&family=JetBrains+Mono:wght@600&display=swap');

/* ---- MAIN APP BACKGROUND ---- */
.stApp {
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%) !important;
  font-family: 'Space Grotesk', -apple-system, sans-serif !important;
  color: #e0e7ff !important;
}

/* Animated aurora overlay */
.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  background:
    radial-gradient(circle at 20% 30%, rgba(120,80,255,0.18), transparent 45%),
    radial-gradient(circle at 80% 70%, rgba(0,200,255,0.14), transparent 45%),
    radial-gradient(circle at 50% 90%, rgba(255,0,150,0.10), transparent 50%);
  animation: auroraBG 12s ease-in-out infinite alternate;
  pointer-events: none;
  z-index: 0;
}
@keyframes auroraBG {
  0% { transform: scale(1) rotate(0deg); opacity: 0.8; }
  100% { transform: scale(1.2) rotate(8deg); opacity: 1; }
}

/* Floating ambient orbs */
.stApp::after {
  content: "";
  position: fixed;
  inset: 0;
  background-image:
    radial-gradient(circle, rgba(147,197,253,0.4) 1px, transparent 1px),
    radial-gradient(circle, rgba(213,0,249,0.3) 1px, transparent 1px);
  background-size: 80px 80px, 120px 120px;
  background-position: 0 0, 40px 60px;
  animation: floatOrbs 30s linear infinite;
  pointer-events: none;
  z-index: 0;
  opacity: 0.4;
}
@keyframes floatOrbs {
  from { transform: translate(0, 0); }
  to   { transform: translate(80px, 120px); }
}

/* Make content sit above the aurora */
.main, .block-container { position: relative; z-index: 1; }
.block-container { padding-top: 1.5rem !important; }

/* ---- HEADINGS ---- */
h1, h2, h3, h4, h5, h6 {
  font-family: 'Space Grotesk', sans-serif !important;
  color: #f0f4ff !important;
  text-shadow: 0 0 30px rgba(147,197,253,0.4);
  letter-spacing: -0.02em;
}
h1 { font-size: 2.4rem !important; font-weight: 800 !important;
     background: linear-gradient(135deg, #67e8f9, #a78bfa, #f472b6);
     -webkit-background-clip: text; -webkit-text-fill-color: transparent;
     background-clip: text;
     filter: drop-shadow(0 0 20px rgba(167,139,250,0.4));
}
h3 { font-weight: 600 !important; }

/* ---- PARAGRAPH TEXT ---- */
p, span, label, div[data-testid="stMarkdownContainer"] {
  color: #c7d2fe !important;
  font-family: 'Space Grotesk', sans-serif;
}

/* ---- METRICS (glassmorphism) ---- */
div[data-testid="stMetric"] {
  background: rgba(30, 27, 75, 0.5) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(147,197,253,0.18) !important;
  border-radius: 16px !important;
  padding: 14px !important;
  box-shadow:
    0 4px 20px rgba(0,0,0,0.3),
    inset 0 1px 0 rgba(255,255,255,0.08);
  transition: transform 0.2s;
}
div[data-testid="stMetric"]:hover {
  transform: translateY(-2px);
  border-color: rgba(147,197,253,0.35) !important;
  box-shadow: 0 8px 30px rgba(103,232,249,0.2), inset 0 1px 0 rgba(255,255,255,0.12);
}
div[data-testid="stMetricLabel"] {
  color: #a5b4fc !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-size: 0.72rem !important;
}
div[data-testid="stMetricValue"] {
  color: #67e8f9 !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-weight: 700 !important;
  text-shadow: 0 0 16px rgba(103,232,249,0.6);
}
div[data-testid="stMetricDelta"] {
  color: #34d399 !important;
}

/* ---- BUTTONS ---- */
.stButton > button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  border: none !important;
  border-radius: 12px !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-weight: 700 !important;
  padding: 0.6rem 1.2rem !important;
  transition: all 0.2s ease !important;
  box-shadow:
    0 4px 16px rgba(102,126,234,0.4),
    inset 0 1px 0 rgba(255,255,255,0.2) !important;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}
.stButton > button:hover {
  transform: translateY(-2px) !important;
  box-shadow:
    0 8px 28px rgba(102,126,234,0.7),
    0 0 20px rgba(167,139,250,0.4),
    inset 0 1px 0 rgba(255,255,255,0.3) !important;
  background: linear-gradient(135deg, #7c8ff0 0%, #8a5bb8 100%) !important;
}
.stButton > button:active {
  transform: translateY(0) !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #ff6b35, #f7b32b) !important;
  box-shadow: 0 4px 20px rgba(255,107,53,0.5) !important;
}

/* ---- SIDEBAR ---- */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(15,12,41,0.95), rgba(48,43,99,0.95)) !important;
  border-right: 1px solid rgba(147,197,253,0.15) !important;
  backdrop-filter: blur(10px);
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
  color: #f0f4ff !important;
}
section[data-testid="stSidebar"] .stRadio label {
  background: rgba(30,27,75,0.5);
  border-radius: 10px;
  padding: 8px 12px !important;
  margin: 3px 0 !important;
  transition: all 0.15s;
  border: 1px solid transparent;
}
section[data-testid="stSidebar"] .stRadio label:hover {
  background: rgba(102,126,234,0.25);
  border-color: rgba(147,197,253,0.3);
}
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) {
  background: linear-gradient(135deg, rgba(102,126,234,0.4), rgba(118,75,162,0.4));
  border-color: rgba(167,139,250,0.6);
  box-shadow: 0 0 20px rgba(167,139,250,0.3);
}

/* ---- ALERTS / INFO / SUCCESS ---- */
.stAlert {
  background: rgba(30,27,75,0.6) !important;
  border-radius: 12px !important;
  border-left: 4px solid #667eea !important;
  backdrop-filter: blur(10px);
  color: #e0e7ff !important;
}
div[data-baseweb="notification"] {
  background: rgba(30,27,75,0.7) !important;
  border-radius: 12px !important;
}

/* ---- PROGRESS BAR ---- */
.stProgress > div > div > div > div {
  background: linear-gradient(90deg, #667eea, #a78bfa, #f472b6) !important;
  box-shadow: 0 0 12px rgba(167,139,250,0.6);
}
.stProgress > div > div {
  background: rgba(30,27,75,0.7) !important;
  border-radius: 8px;
}

/* ---- DIVIDER ---- */
hr {
  border: none !important;
  height: 1px !important;
  background: linear-gradient(90deg, transparent, rgba(147,197,253,0.3), transparent) !important;
  margin: 1.5rem 0 !important;
}

/* ---- TOASTS ---- */
div[data-testid="stToast"] {
  background: rgba(30,27,75,0.9) !important;
  color: #e0e7ff !important;
  border: 1px solid rgba(147,197,253,0.3) !important;
  border-radius: 12px !important;
  backdrop-filter: blur(12px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.4), 0 0 20px rgba(167,139,250,0.3) !important;
}

/* ---- SCROLLBAR ---- */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: rgba(15,12,41,0.5); }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #667eea, #764ba2);
  border-radius: 10px;
  border: 2px solid rgba(15,12,41,0.5);
}
::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #7c8ff0, #8a5bb8);
}

/* ---- SELECTBOX / INPUT ---- */
.stSelectbox > div > div,
.stTextInput > div > div > input {
  background: rgba(30,27,75,0.6) !important;
  color: #e0e7ff !important;
  border-color: rgba(147,197,253,0.3) !important;
  border-radius: 10px !important;
}

/* ---- EXPANDER ---- */
.streamlit-expanderHeader {
  background: rgba(30,27,75,0.5) !important;
  border-radius: 10px !important;
  color: #e0e7ff !important;
}

/* ---- TABS ---- */
.stTabs [data-baseweb="tab"] {
  background: rgba(30,27,75,0.5);
  border-radius: 10px;
  color: #a5b4fc;
  border: 1px solid transparent;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(102,126,234,0.5), rgba(118,75,162,0.5)) !important;
  color: white !important;
  border-color: rgba(167,139,250,0.6) !important;
  box-shadow: 0 0 16px rgba(167,139,250,0.3);
}

/* ---- CAPTIONS ---- */
.stCaption, small {
  color: #94a3b8 !important;
  font-style: italic;
}

/* ---- FROG FLASH TEXT ---- */
.flash-text {
  font-size: 1.6rem;
  text-align: center;
  font-weight: 800;
  background: linear-gradient(90deg, #f472b6, #a78bfa, #67e8f9);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
  filter: drop-shadow(0 0 16px rgba(167,139,250,0.6));
  animation: flashPop 0.4s ease-out;
}
@keyframes flashPop {
  0% { transform: scale(0.8); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

/* ---- SHOP CARD STYLE ---- */
.shop-card {
  background: rgba(30,27,75,0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(147,197,253,0.18);
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  transition: all 0.2s;
}
.shop-card:hover {
  border-color: rgba(167,139,250,0.5);
  box-shadow: 0 0 30px rgba(167,139,250,0.3);
  transform: translateY(-4px);
}
</style>
"""
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ============================================================
# Now paste ALL of your existing code from the previous app.py
# (declare_component, sounds, frog, balloon, save, achievements, shop, play)
# ============================================================
