# frontpage.py
import streamlit as st
import cv2
import mediapipe as mp
import time
import numpy as np

from backend.engine import init_state, step_frame

# =========================================================
# CONFIG
# =========================================================
WIDTH, HEIGHT = 800, 600
st.set_page_config(page_title="Jungle Snake Adventure", layout="wide")

# =========================================================
# SESSION STATE INIT
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "instructions"

if "intro_loaded" not in st.session_state:
    st.session_state.intro_loaded = False

if "cap" not in st.session_state:
    st.session_state.cap = None

# =========================================================
# INTRO EFFECTS (LOAD ONLY ONCE — CRITICAL)
# =========================================================
if not st.session_state.intro_loaded:
    st.markdown("""
    <style>
    body { overflow: hidden; }

    #layer1,#layer2,#layer3 {
        position: fixed; width:110%; height:110%; top:-5%; left:-5%;
        background-size:cover; z-index:-50;
    }
    #layer1 { background-image:url('https://i.imgur.com/3j9QjRA.jpg'); animation: move1 60s linear infinite; }
    #layer2 { background-image:url('https://i.imgur.com/tZxIVvO.png'); animation: move2 40s linear infinite; }
    #layer3 { background-image:url('https://i.imgur.com/6KtxFef.png'); animation: move3 25s linear infinite; }

    @keyframes move1 { to{transform:translateX(-80px)} }
    @keyframes move2 { to{transform:translateX(-180px)} }
    @keyframes move3 { to{transform:translateX(-260px)} }

    .fog {
        position:fixed; width:130%; height:130%; top:-10%; left:-10%;
        background:url('https://i.imgur.com/qL7Wk2R.png'); opacity:.18;
        animation:fogMove 35s linear infinite; z-index:-20;
    }
    @keyframes fogMove { 50%{transform:translateX(8%)} }

    .firefly {
        position:fixed; width:6px; height:6px; border-radius:50%;
        background:radial-gradient(circle,#ffffaa,#ffaa00,transparent);
        animation:flyfire linear infinite; z-index:-10;
    }
    @keyframes flyfire {
        50%{transform:translate(30px,-50px) scale(1.3);opacity:1}
    }

    .leaf {
        position:fixed; top:-60px; width:45px; height:45px;
        background:url('https://i.imgur.com/mXBo47X.png'); background-size:cover;
        animation:fall linear infinite; z-index:-15;
    }
    @keyframes fall { to{transform:translateY(120vh) rotate(360deg)} }

    .instr-panel {
        background:rgba(0,0,0,.55); padding:24px; border-radius:14px;
        box-shadow:0 10px 40px rgba(0,0,0,.7); color:#eaffea;
    }

    .stButton > button {
        animation:pulse 2s infinite; border-radius:12px;
    }
    @keyframes pulse {
        50%{box-shadow:0 0 30px #00ffee}
    }
    </style>

    <div id="layer1"></div><div id="layer2"></div><div id="layer3"></div>
    <div class="fog"></div>
    """, unsafe_allow_html=True)

    # Fireflies & leaves
    fx = ""
    for _ in range(12):
        fx += f'<div class="firefly" style="left:{np.random.randint(5,95)}%;top:{np.random.randint(5,95)}%;animation-duration:{np.random.uniform(6,14):.1f}s"></div>'
    for _ in range(8):
        fx += f'<div class="leaf" style="left:{np.random.randint(0,100)}%;animation-duration:{np.random.randint(8,18)}s"></div>'
    st.markdown(fx, unsafe_allow_html=True)

    # Ambient audio
    st.markdown("""
    <audio autoplay loop>
      <source src="https://cdn.pixabay.com/download/audio/2021/09/16/audio_2cb35c50e9.mp3" type="audio/mpeg">
    </audio>
    """, unsafe_allow_html=True)

    st.session_state.intro_loaded = True

# =========================================================
# LAYOUT
# =========================================================
left_col, right_col = st.columns([3, 2])
GAME_FRAME = left_col.container()
CAMERA_FRAME = right_col.container()

# =========================================================
# INSTRUCTION PAGE
# =========================================================
if st.session_state.page == "instructions":

    left_col.markdown("""
    <div class="instr-panel">
    <h1 style="text-align:center">🌴 JUNGLE SNAKE ADVENTURE 🐍</h1>
    <ul style="font-size:18px;line-height:1.8">
      <li>🖐 Raise your <b>index finger</b> to control the snake</li>
      <li>🍎 Red fruit = +1</li>
      <li>🟡 Gold fruit = +5</li>
      <li>⚡ Blue orb = speed boost</li>
      <li>👁 White orb = invisibility</li>
      <li>💥 Avoid walls & obstacles</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    start = left_col.button("🚀 START GAME", use_container_width=True)

    right_col.markdown("### 🎛 Quick Settings")
    st.session_state.theme = right_col.selectbox(
        "Theme", ["Neon", "Dark", "Forest", "Fire"], index=0
    )

    if not start:
        CAMERA_FRAME.markdown("🎬 Waiting to start…")
        st.stop()

    # INIT GAME
    st.session_state.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    for _ in range(3):  # camera warmup
        st.session_state.cap.read()

    mp_hands = mp.solutions.hands
    st.session_state.hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    st.session_state.state = init_state(WIDTH, HEIGHT)
    st.session_state.page = "game"
    time.sleep(0.2)
    st.rerun()

# =========================================================
# GAME PAGE (NO BLINKING)
# =========================================================
if st.session_state.page == "game":

    cap = st.session_state.cap
    hands = st.session_state.hands
    state = st.session_state.state

    ret, frame = cap.read()
    if not ret:
        st.error("Camera error")
        st.stop()

    frame = cv2.flip(frame, 1)

    with CAMERA_FRAME:
        st.image(frame, channels="BGR")

    resized = cv2.resize(frame, (WIDTH, HEIGHT))
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    rgb_out, state, delay = step_frame(
        rgb, results, state,
        theme_name=st.session_state.theme,
        width=WIDTH, height=HEIGHT
    )

    st.session_state.state = state

    with GAME_FRAME:
        st.image(rgb_out, channels="RGB")

    time.sleep(delay)
    st.rerun()
