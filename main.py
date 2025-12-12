import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import random
import math
import time

# -----------------------------------------------------------
# IMPORT INSTRUCTION SCREEN
# -----------------------------------------------------------
from instructions import show_instructions

# -----------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------
st.set_page_config(page_title="Hand Snake Game", layout="wide")
st.title("🖐️ Hand-Controlled Snake Game (Advanced Version)")

FRAME = st.empty()  # Camera output placeholder

WIDTH, HEIGHT = 800, 600

# -----------------------------------------------------------
# STEP 1: SHOW INSTRUCTION PAGE FIRST
# -----------------------------------------------------------
if "showing_instructions" not in st.session_state:
    st.session_state.showing_instructions = True

# If user has not clicked START yet → show instructions
if st.session_state.showing_instructions:
    start = show_instructions()
    if not start:
        st.stop()
    else:
        st.session_state.showing_instructions = False  # Move to game
        st.rerun()


# -----------------------------------------------------------
# SIMPLE SOUND PLAYER (browser audio)
# -----------------------------------------------------------
def play_sound(sound_id: int):
    sound_html = f"""
    <audio autoplay>
        <source src="https://assets.mixkit.co/sfx/preview/mixkit-{sound_id}.mp3" type="audio/mpeg">
    </audio>
    """
    st.markdown(sound_html, unsafe_allow_html=True)

# Sound IDs
SND_EAT_NORMAL = 1172
SND_EAT_GOLD   = 1173
SND_BOOST      = 1717
SND_GAME_OVER  = 1389

# -----------------------------------------------------------
# SESSION STATE INIT
# -----------------------------------------------------------
if "snake_pos" not in st.session_state:
    st.session_state.snake_pos = [100.0, 50.0]
    st.session_state.snake_body = [[100.0, 50.0], [90.0, 50.0], [80.0, 50.0]]
    st.session_state.score = 0
    st.session_state.high_score = 0
    st.session_state.food_pos = [400, 300]
    st.session_state.food_kind = "normal"
    st.session_state.game_started = False
    st.session_state.game_over = False
    st.session_state.level = 1
    st.session_state.paused = False

    # Obstacles
    st.session_state.obstacles = [
        [WIDTH // 2, HEIGHT // 3, 25],
        [WIDTH // 3, 2 * HEIGHT // 3, 25],
        [2 * WIDTH // 3, HEIGHT // 2, 25]
    ]

    st.session_state.obstacle_vel = [[2, 2], [-2, 2], [2, -2]]

    # Power-ups
    st.session_state.blue_food_pos = None
    st.session_state.speed_boost_active = False
    st.session_state.speed_boost_timer = 0.0

    st.session_state.invisible_food_pos = None
    st.session_state.invisible_active = False
    st.session_state.invisible_timer = 0.0

    # Boss
    st.session_state.boss_active = False
    st.session_state.boss_pos = [WIDTH // 2, HEIGHT // 2]

    st.session_state.game_over_sound_played = False

# -----------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------
def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def spawn_food():
    while True:
        x = random.randint(20, WIDTH - 20)
        y = random.randint(20, HEIGHT - 20)
        if all(dist([x, y], block) > 25 for block in st.session_state.snake_body):
            kind = "gold" if random.random() < 0.2 else "normal"
            return [x, y], kind

def reset_game():
    st.session_state.snake_pos = [100.0, 50.0]
    st.session_state.snake_body = [[100.0, 50.0], [90.0, 50.0], [80.0, 50.0]]
    st.session_state.score = 0
    st.session_state.level = 1
    st.session_state.food_pos, st.session_state.food_kind = spawn_food()
    st.session_state.game_started = False
    st.session_state.game_over = False
    st.session_state.blue_food_pos = None
    st.session_state.speed_boost_active = False
    st.session_state.invisible_food_pos = None
    st.session_state.invisible_active = False
    st.session_state.game_over_sound_played = False
    st.session_state.boss_active = False
    st.session_state.boss_pos = [WIDTH // 2, HEIGHT // 2]

def rainbow_color(t):
    r = int(128 + 127 * math.sin(t))
    g = int(128 + 127 * math.sin(t + 2))
    b = int(128 + 127 * math.sin(t + 4))
    return (r, g, b)

particle_list = []

# -----------------------------------------------------------
# CAMERA + MEDIAPIPE
# -----------------------------------------------------------
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)

# -----------------------------------------------------------
# GAME LOOP
# -----------------------------------------------------------
while True:

    ret, frame = cap.read()
    if not ret:
        st.error("Camera not available")
        break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    snake_pos = st.session_state.snake_pos
    snake_body = st.session_state.snake_body
    score = st.session_state.score
    high_score = st.session_state.high_score
    food_pos = st.session_state.food_pos
    food_kind = st.session_state.food_kind
    game_over = st.session_state.game_over
    game_started = st.session_state.game_started
    level = st.session_state.level
    obstacles = st.session_state.obstacles
    vel = st.session_state.obstacle_vel

    blue_food = st.session_state.blue_food_pos
    speed_boost_active = st.session_state.speed_boost_active
    invisible_food = st.session_state.invisible_food_pos
    invisible_active = st.session_state.invisible_active

    delay = max(0.015, 0.04 - (level - 1) * 0.003)
    smoothing = min(0.20, 0.12 + (level - 1) * 0.01)

    if speed_boost_active:
        smoothing = 0.28
        delay = max(0.01, delay * 0.6)

    # -----------------------------------------------------------
    # START SCREEN BEFORE GAME ACTUALLY STARTS
    # -----------------------------------------------------------
    if not game_started and not game_over:
        cv2.putText(rgb, "Show your hand to START",
                    (130, HEIGHT // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                    (255, 255, 255), 2)

        FRAME.image(rgb, channels="RGB")

        if results.multi_hand_landmarks:
            st.session_state.game_started = True

        time.sleep(0.03)
        continue

    # -----------------------------------------------------------
    # GAME RUNNING
    # -----------------------------------------------------------
    elif game_started and not game_over:

        # Hand tracking
        if results.multi_hand_landmarks:
            lm = results.multi_hand_landmarks[0].landmark[8]
            x, y = int(lm.x * WIDTH), int(lm.y * HEIGHT)
            snake_pos[0] += (x - snake_pos[0]) * smoothing
            snake_pos[1] += (y - snake_pos[1]) * smoothing

        # Snake body
        snake_body.insert(0, list(snake_pos))
        if len(snake_body) > score + 3:
            snake_body.pop()

        # Moving obstacles
        for i, obs in enumerate(obstacles):
            ox, oy, r = obs
            vx, vy = vel[i]
            ox += vx
            oy += vy
            if ox < r or ox > WIDTH - r:
                vx *= -1
            if oy < r or oy > HEIGHT - r:
                vy *= -1
            vel[i] = [vx, vy]
            obstacles[i] = [ox, oy, r]
            cv2.circle(rgb, (int(ox), int(oy)), r, (140, 140, 140), -1)

        # BLUE SPEED BOOST
        if blue_food is None and random.random() < 0.01:
            st.session_state.blue_food_pos = [
                random.randint(20, WIDTH - 20),
                random.randint(20, HEIGHT - 20)
            ]
            blue_food = st.session_state.blue_food_pos

        if blue_food:
            cv2.circle(rgb, (int(blue_food[0]), int(blue_food[1])), 10, (0, 128, 255), -1)
            if dist(snake_pos, blue_food) < 20:
                st.session_state.speed_boost_active = True
                st.session_state.speed_boost_timer = time.time()
                st.session_state.blue_food_pos = None
                play_sound(SND_BOOST)

        if speed_boost_active and time.time() - st.session_state.speed_boost_timer > 7:
            st.session_state.speed_boost_active = False

        # INVISIBLE ORB
        if invisible_food is None and random.random() < 0.005:
            st.session_state.invisible_food_pos = [
                random.randint(20, WIDTH - 20),
                random.randint(20, HEIGHT - 20)
            ]
            invisible_food = st.session_state.invisible_food_pos

        if invisible_food:
            cv2.circle(rgb, (int(invisible_food[0]), int(invisible_food[1])), 10, (255, 255, 255), 2)
            if dist(snake_pos, invisible_food) < 20:
                st.session_state.invisible_active = True
                st.session_state.invisible_timer = time.time()
                st.session_state.invisible_food_pos = None
                play_sound(SND_BOOST)

        if invisible_active and time.time() - st.session_state.invisible_timer > 6:
            st.session_state.invisible_active = False

        # FOOD
        if dist(snake_pos, food_pos) < 20:
            if food_kind == "gold":
                score += 5
                play_sound(SND_EAT_GOLD)
            else:
                score += 1
                play_sound(SND_EAT_NORMAL)
            st.session_state.food_pos, st.session_state.food_kind = spawn_food()
            food_pos = st.session_state.food_pos
            food_kind = st.session_state.food_kind

        color = (255, 215, 0) if food_kind == "gold" else (255, 0, 0)
        cv2.circle(rgb, (int(food_pos[0]), int(food_pos[1])), 10, color, -1)

        # BOSS
        if level >= 10 and not st.session_state.boss_active:
            st.session_state.boss_active = True

        if st.session_state.boss_active:
            bx, by = st.session_state.boss_pos
            bx += (snake_pos[0] - bx) * 0.01
            by += (snake_pos[1] - by) * 0.01
            st.session_state.boss_pos = [bx, by]
            cv2.circle(rgb, (int(bx), int(by)), 60, (0, 0, 255), -1)
            cv2.circle(rgb, (int(bx), int(by)), 80, (255, 0, 0), 3)
            if dist(snake_pos, [bx, by]) < 70:
                game_over = True

        # PARTICLES + SNAKE
        particle_list.append([snake_pos[0], snake_pos[1], 15])
        for p in particle_list[:]:
            px, py, pr = p
            cv2.circle(rgb, (int(px), int(py)), pr, (0, 255, 150), 1)
            p[2] -= 1
            if p[2] <= 0:
                particle_list.remove(p)

        for i, block in enumerate(snake_body):
            cv2.circle(rgb, (int(block[0]), int(block[1])), 15, (0, 255, 0), 2)
            col = (0, 255, 100) if i == 0 else (0, 255, 0)
            cv2.circle(rgb, (int(block[0]), int(block[1])), 10, col, -1)

        # HUD
        t = time.time()
        rainbow = rainbow_color(t)
        cv2.putText(rgb, f"Score: {score}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, rainbow, 3)
        cv2.putText(rgb, f"High: {high_score}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,215,0), 2)

        level = 1 + score // 5
        st.session_state.level = level
        cv2.putText(rgb, f"Level: {level}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,200,255), 2)

        progress = (score % 5) / 5.0
        bar_w = int(progress * 200)
        cv2.rectangle(rgb, (20, 150), (220, 170), (50, 50, 50), -1)
        cv2.rectangle(rgb, (20, 150), (20 + bar_w, 170), (0, 200, 255), -1)

        # COLLISIONS
        if snake_pos[0] < 0 or snake_pos[0] > WIDTH or snake_pos[1] < 0 or snake_pos[1] > HEIGHT:
            game_over = True

        if not invisible_active:
            for ox, oy, r in obstacles:
                if dist(snake_pos, [ox, oy]) < r + 10:
                    game_over = True
                    break
            if not game_over:
                for block in snake_body[4:]:
                    if dist(snake_pos, block) < 10:
                        game_over = True
                        break

        st.session_state.snake_body = snake_body
        st.session_state.snake_pos = snake_pos
        st.session_state.score = score
        st.session_state.game_over = game_over

    # -----------------------------------------------------------
    # GAME OVER
    # -----------------------------------------------------------
    if game_over:
        if score > high_score:
            st.session_state.high_score = score

        if not st.session_state.game_over_sound_played:
            play_sound(SND_GAME_OVER)
            st.session_state.game_over_sound_played = True

        cv2.putText(rgb, "GAME OVER!", (WIDTH // 2 - 150, HEIGHT // 2 - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255,50,50), 3)
        cv2.putText(rgb, "Show your hand to restart",
                    (WIDTH // 2 - 200, HEIGHT // 2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

        if results.multi_hand_landmarks:
            reset_game()

    FRAME.image(rgb, channels="RGB")
    time.sleep(delay)
