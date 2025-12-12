# frontpage.py
import streamlit as st
import cv2
import mediapipe as mp
import time
import numpy as np

from backend.engine import init_state, step_frame

# -------------------------
# Config
# -------------------------
WIDTH, HEIGHT = 800, 600
st.set_page_config(page_title="Jungle Snake Adventure", layout="wide")

# -------------------------
# Premium Intro Effects (Parallax, Fog, Fireflies, Leaves, Thunder, Audio)
# Put this right after page config
# -------------------------
st.markdown("""
<style>
/* basic cleanup */
body { overflow: hidden; }

/* Parallax layers */
#layer1,#layer2,#layer3 {
    position: fixed; width: 110%; height: 110%; top: -5%; left: -5%;
    background-size: cover; background-repeat: no-repeat; z-index: -50;
}
#layer1 { background-image: url('https://i.imgur.com/3j9QjRA.jpg'); animation: move1 60s linear infinite; opacity: 1; }
#layer2 { background-image: url('https://i.imgur.com/tZxIVvO.png'); animation: move2 40s linear infinite; opacity: 0.9; }
#layer3 { background-image: url('https://i.imgur.com/6KtxFef.png'); animation: move3 25s linear infinite; opacity: 1.0; }

@keyframes move1 { from{transform:translateX(0)} to{transform:translateX(-80px);} }
@keyframes move2 { from{transform:translateX(0)} to{transform:translateX(-180px);} }
@keyframes move3 { from{transform:translateX(0)} to{transform:translateX(-260px);} }

/* Fog */
.fog {
    position: fixed; top: -10%; left: -10%; width: 130%; height: 130%;
    background-image: url('https://i.imgur.com/qL7Wk2R.png'); opacity: 0.20;
    animation: fogMove 35s linear infinite; pointer-events:none; z-index:-20;
}
@keyframes fogMove { 0%{transform:translateX(-5%)} 50%{transform:translateX(8%)} 100%{transform:translateX(-5%)} }

/* Fireflies */
.firefly {
    position: fixed; width: 6px; height: 6px; border-radius:50%;
    background: radial-gradient(circle,#ffffaa 0%,#ffaa00 60%,transparent 100%);
    pointer-events:none; animation: flyfire linear infinite; z-index:-10;
}
@keyframes flyfire { 0%{transform:translate(0,0) scale(1);opacity:0.5} 50%{transform:translate(30px,-50px) scale(1.3);opacity:1} 100%{transform:translate(-20px,20px) scale(1);opacity:0.5} }

/* Leaves */
.leaf {
    position: fixed; top:-60px; width:45px; height:45px;
    background-image: url('https://i.imgur.com/mXBo47X.png'); background-size:cover;
    pointer-events:none; opacity:0.85; animation: fall linear infinite; z-index:-15;
}
@keyframes fall { 0%{transform:translateY(0) rotate(0deg)} 100%{transform:translateY(120vh) rotate(360deg)} }

/* Thunder flash */
#thunder {
    position: fixed; top:0; left:0; width:100vw; height:100vh; background:white; opacity:0;
    z-index:-5; animation: lightningFlash 15s infinite;
}
@keyframes lightningFlash {
    0%, 92%, 100% { opacity: 0; }
    93% { opacity: 0.25; }
    94% { opacity: 0; }
    96% { opacity: 0.18; }
    97% { opacity: 0; }
}

/* Snake slide */
.snake-slide {
    position: fixed; bottom: 8px; left: -260px; width: 260px; opacity:0.95;
    filter: drop-shadow(0 0 18px #00ffaa); animation: snakeMove 20s linear infinite; z-index:-10; pointer-events:none;
}
@keyframes snakeMove { 0%{left:-260px} 50%{left:110%} 100%{left:-260px} }

/* Title shine (for when we show page title) */
.title-shine { position: relative; display: inline-block; }
.title-shine:after {
    content: ""; position: absolute; top:0; left:-150%; width:50%; height:100%;
    background: linear-gradient(120deg, transparent, rgba(255,255,255,0.45), transparent);
    animation: shine 3s ease-in-out infinite;
}
@keyframes shine { 0%{left:-150%} 50%{left:150%} 100%{left:-150%} }

/* Start button pulse */
.stButton > button { animation: pulse 2s infinite; border-radius:12px; }
@keyframes pulse { 0%{box-shadow:0 0 10px #00ffcc} 50%{box-shadow:0 0 35px #00ffee} 100%{box-shadow:0 0 10px #00ffcc} }

/* Instruction card */
.instr-panel {
    margin: 20px auto; max-width: 920px;
    background: rgba(0,0,0,0.55); border-radius: 12px; padding: 24px;
    color: #e9ffe9; box-shadow: 0 8px 40px rgba(0,0,0,0.6);
    border: 1px solid rgba(255,255,255,0.04);
}
.instr-title { font-size: 36px; font-weight:800; color:#aaffcc; text-align:center; margin-bottom:8px; text-shadow:0 0 8px #003300; }
.instr-list { font-size:18px; line-height:1.9; color:#f0fff0; }
</style>

<!-- Parallax -->
<div id="layer1"></div>
<div id="layer2"></div>
<div id="layer3"></div>

<!-- Fog, thunder and snake -->
<div class="fog"></div>
<div id="thunder"></div>
<img class="snake-slide" src="https://i.imgur.com/0lx5M0w.png" alt="snake-slide">

<!-- Fireflies and leaves inserted dynamically below -->
""", unsafe_allow_html=True)

# Add some fireflies & leaves HTML via Python (random positions/speeds)
_fire_html = ""
for i in range(14):
    _fire_html += f'<div class="firefly" style="left:{np.random.randint(2,98)}%; top:{np.random.randint(2,98)}%; animation-duration:{np.random.uniform(6,14):.1f}s;"></div>'
for i in range(10):
    _fire_html += f'<div class="leaf" style="left:{np.random.randint(0,100)}%; animation-duration:{np.random.randint(8,18)}s; animation-delay:{np.random.randint(0,10)}s;"></div>'
st.markdown(_fire_html, unsafe_allow_html=True)

# Jungle ambient audio (optional, URL-hosted)
st.markdown("""
<audio autoplay loop>
  <source src="https://cdn.pixabay.com/download/audio/2021/09/16/audio_2cb35c50e9.mp3?filename=jungle-ambient.mp3" type="audio/mpeg">
</audio>
""", unsafe_allow_html=True)


# -------------------------
# Layout: left = game, right = camera + controls
# -------------------------
left_col, right_col = st.columns([3, 2])
GAME_FRAME = left_col.empty()
CAMERA_FRAME = right_col.empty()

# Instruction card (centered)
if "page" not in st.session_state:
    st.session_state.page = "instructions"

if st.session_state.page == "instructions":
    # Instruction content (styled panel)
    st.markdown('<div class="instr-panel">', unsafe_allow_html=True)
    st.markdown('<div class="instr-title title-shine">🌴 JUNGLE SNAKE ADVENTURE 🐍</div>', unsafe_allow_html=True)

    left_col.markdown(
        """
        <div class="instr-list">
        <ul>
          <li>🖐 <b>Raise your index finger</b> to control the snake.</li>
          <li>🍎 Eat red fruits to grow (+1).</li>
          <li>🟡 Eat golden fruits for big bonus (+5).</li>
          <li>⚡ Blue orb gives speed boost for short time.</li>
          <li>👁 White orb grants invisibility for a few seconds.</li>
          <li>💥 Avoid obstacles & walls — boss appears at Level 10.</li>
          <li>🍀 Teleporting fruit: when you get close, food may teleport (fun challenge).</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Start button (single key; won't duplicate)
    start = left_col.button("🚀 START GAME", key="premium_start_btn", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close instr-panel

    # Right column smaller instructions / theme
    right_col.markdown("### ▶ Quick Settings")
    if "theme" not in st.session_state:
        st.session_state.theme = "Neon"
    st.session_state.theme = right_col.selectbox(
        "Theme", ["Neon", "Dark", "Forest", "Fire"], index=["Neon", "Dark", "Forest", "Fire"].index(st.session_state.theme)
    )

    right_col.markdown("**Tip:** Click START to activate the camera & begin playing.")

    if not start:
        # show an attractive fullscreen-ish preview shot on left (we already have parallax background)
        CAMERA_FRAME.markdown("🎬 Waiting to start — preview the jungle intro above.")
        st.stop()

    # If start pressed: initialize camera and game state and move to gameplay
    st.session_state.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    mp_hands = mp.solutions.hands
    st.session_state.hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    st.session_state.state = init_state(WIDTH, HEIGHT)
    st.session_state.page = "game"

    # small delay for camera warmup then rerun so gameplay begins next run
    time.sleep(0.25)
    st.rerun()


# -------------------------
# Game page: normal gameplay + right-side live camera
# -------------------------
if st.session_state.page == "game":
    # ensure camera and hands are present
    if "cap" not in st.session_state or st.session_state.cap is None:
        st.error("Camera not initialized.")
        st.stop()

    cap = st.session_state.cap
    hands = st.session_state.hands
    state = st.session_state.state

    # Grab one frame (single-frame-per-run pattern)
    ret, frame = cap.read()
    if not ret:
        GAME_FRAME.error("Camera not available")
        st.stop()

    frame = cv2.flip(frame, 1)
    # show raw camera on right
    CAMERA_FRAME.image(frame, channels="BGR")

    # prepare frame for engine
    resized = cv2.resize(frame, (WIDTH, HEIGHT))
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # run engine for this frame
    rgb_out, state, delay = step_frame(
        rgb, results, state,
        theme_name=st.session_state.get("theme", "Neon"),
        width=WIDTH, height=HEIGHT
    )

    # save state back
    st.session_state.state = state

    # show game on left
    GAME_FRAME.image(rgb_out, channels="RGB")

    # frame pacing: small sleep then rerun for next frame
    time.sleep(delay)
    st.rerun()
