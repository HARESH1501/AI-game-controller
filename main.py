import streamlit as st
import cv2
import mediapipe as mp
import random
import math
import time

# ======================
# Page Config
# ======================
st.set_page_config(page_title="Hand Snake Game", layout="wide")

# ======================
# Session State
# ======================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "running" not in st.session_state:
    st.session_state.running = False

if "cap" not in st.session_state:
    st.session_state.cap = None

if "snake_pos" not in st.session_state:
    st.session_state.snake_pos = [100, 100]
    st.session_state.snake_body = [[100, 100], [90, 100], [80, 100]]
    st.session_state.direction = "RIGHT"
    st.session_state.score = 0
    st.session_state.food = [300, 200]

# ======================
# HOME PAGE
# ======================
if st.session_state.page == "home":

    st.title("✋ Hand-Controlled Snake Game")

    st.markdown("""
### 🎮 How to Play
- Show your hand to the camera  
- Move your **index finger** to control the snake  

### 🍎 Food
- 🔴 Red → +1 score  

### ⚠️ Avoid
- Walls  
- Your own body  

### 💡 Tip
- Good lighting improves tracking
""")

    if st.button("🚀 Start Game", use_container_width=True):
        st.session_state.page = "game"
        st.session_state.running = True
        st.experimental_rerun()

# ======================
# GAME PAGE
# ======================
if st.session_state.page == "game":

    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button("⏹ Stop"):
            if st.session_state.cap:
                st.session_state.cap.release()
                st.session_state.cap = None
            st.session_state.page = "home"
            st.session_state.running = False
            st.experimental_rerun()

    # Open camera once
    if st.session_state.cap is None:
        st.session_state.cap = cv2.VideoCapture(0)

    cap = st.session_state.cap

    # MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1)
    mp_draw = mp.solutions.drawing_utils

    WIDTH, HEIGHT = 640, 480
    frame_area = st.image([])

    # ======================
    # SINGLE FRAME UPDATE
    # ======================
    ret, frame = cap.read()
    if not ret:
        st.error("Camera not working")
        st.stop()

    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    # Hand control
    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            tip = hand.landmark[8]
            x = int(tip.x * WIDTH)
            y = int(tip.y * HEIGHT)

            if abs(x - st.session_state.snake_pos[0]) > abs(y - st.session_state.snake_pos[1]):
                st.session_state.direction = "RIGHT" if x > st.session_state.snake_pos[0] else "LEFT"
            else:
                st.session_state.direction = "DOWN" if y > st.session_state.snake_pos[1] else "UP"

            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

    # Move snake
    if st.session_state.direction == "RIGHT":
        st.session_state.snake_pos[0] += 10
    elif st.session_state.direction == "LEFT":
        st.session_state.snake_pos[0] -= 10
    elif st.session_state.direction == "UP":
        st.session_state.snake_pos[1] -= 10
    elif st.session_state.direction == "DOWN":
        st.session_state.snake_pos[1] += 10

    st.session_state.snake_body.insert(0, list(st.session_state.snake_pos))

    # Food collision
    def dist(a, b):
        return math.hypot(a[0]-b[0], a[1]-b[1])

    if dist(st.session_state.snake_pos, st.session_state.food) < 15:
        st.session_state.score += 1
        st.session_state.food = [
            random.randrange(20, WIDTH-20, 10),
            random.randrange(20, HEIGHT-20, 10)
        ]
    else:
        st.session_state.snake_body.pop()

    # Game over
    if (
        st.session_state.snake_pos[0] < 0 or
        st.session_state.snake_pos[0] > WIDTH or
        st.session_state.snake_pos[1] < 0 or
        st.session_state.snake_pos[1] > HEIGHT or
        st.session_state.snake_pos in st.session_state.snake_body[1:]
    ):
        st.warning("💀 Game Over")
        time.sleep(1)
        st.session_state.page = "home"
        st.experimental_rerun()

    # Draw
    for block in st.session_state.snake_body:
        cv2.rectangle(frame, (block[0], block[1]), (block[0]+10, block[1]+10), (0,255,0), -1)

    f = st.session_state.food
    cv2.rectangle(frame, (f[0], f[1]), (f[0]+10, f[1]+10), (0,0,255), -1)

    cv2.putText(frame, f"Score: {st.session_state.score}", (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    frame_area.image(frame, channels="BGR")

    time.sleep(0.03)
    st.experimental_rerun()
