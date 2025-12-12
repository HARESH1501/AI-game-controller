import time
import cv2
from .utils import dist
from .theme import get_theme_colors
from .snake import move_snake, update_body, draw_snake
from .food import (
    spawn_food, draw_food,
    maybe_spawn_blue, draw_blue_food,
    maybe_spawn_invisible, draw_invisible,
)
from .obstacles import update_obstacles, draw_obstacles
from .boss import update_boss, draw_boss, boss_hits_snake
from .sounds import play_sound, SND_EAT_NORMAL, SND_EAT_GOLD, SND_BOOST, SND_GAME_OVER


# -----------------------------------------------------------
# INITIAL GAME STATE
# -----------------------------------------------------------
def init_state(width, height):
    return {
        "snake_pos": [100.0, 50.0],
        "snake_body": [[100.0, 50.0], [90.0, 50.0], [80.0, 50.0]],
        "score": 0,
        "high_score": 0,  # NEVER reset unless exceeded
        "food_pos": [width // 2, height // 2],
        "food_kind": "normal",
        "game_started": False,
        "game_over": False,
        "level": 1,

        # Obstacles
        "obstacles": [
            [width // 2, height // 3, 25],
            [width // 3, 2 * height // 3, 25],
            [2 * width // 3, height // 2, 25],
        ],
        "obstacle_vel": [[2, 2], [-2, 2], [2, -2]],

        # Power-ups
        "blue_food_pos": None,
        "speed_boost_active": False,
        "speed_boost_timer": 0.0,
        "invisible_food_pos": None,
        "invisible_active": False,
        "invisible_timer": 0.0,

        # Boss
        "boss_active": False,
        "boss_pos": [width // 2, height // 2],

        "game_over_sound_played": False,
        "particles": [],
    }


# -----------------------------------------------------------
# MAIN FRAME UPDATE FUNCTION
# -----------------------------------------------------------
def step_frame(rgb, results, state, theme_name="Neon", width=800, height=600):
    """Updates everything per frame & draws the game."""
    colors = get_theme_colors(theme_name)

    snake_pos = state["snake_pos"]
    snake_body = state["snake_body"]
    score = state["score"]
    food_pos = state["food_pos"]
    food_kind = state["food_kind"]
    game_started = state["game_started"]
    game_over = state["game_over"]
    level = state["level"]
    obstacles = state["obstacles"]
    vel = state["obstacle_vel"]

    blue_food = state["blue_food_pos"]
    invisible_food = state["invisible_food_pos"]
    speed_boost_active = state["speed_boost_active"]
    invisible_active = state["invisible_active"]

    particles = state["particles"]

    # Movement speed settings
    delay = max(0.015, 0.04 - (level - 1) * 0.003)
    smoothing = min(0.20, 0.12 + (level - 1) * 0.01)

    if speed_boost_active:
        smoothing = 0.28
        delay = max(0.01, delay * 0.6)

    # -----------------------------------------------------------
    # BACKGROUND + WALL BORDER
    # -----------------------------------------------------------
    cv2.rectangle(rgb, (0, 0), (width, height), colors["bg"], -1)
    cv2.rectangle(rgb, (5, 5), (width - 5, height - 5), colors["wall"], 3)

    # -----------------------------------------------------------
    # BEFORE GAME START — WAIT FOR HAND
    # -----------------------------------------------------------
    if not game_started and not game_over:
        cv2.putText(rgb, "Show your hand to START",
                    (140, height // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                    (255, 255, 255), 2)

        if results.multi_hand_landmarks:
            state["game_started"] = True

        return rgb, state, delay

    # -----------------------------------------------------------
    # GAME RUNNING
    # -----------------------------------------------------------
    if game_started and not game_over:

        # ---- HAND TRACKING ----
        if results.multi_hand_landmarks:
            lm = results.multi_hand_landmarks[0].landmark[8]
            x = int(lm.x * width)
            y = int(lm.y * height)
            move_snake(snake_pos, x, y, smoothing)

        # Update snake body
        update_body(snake_body, snake_pos, score)

        # ---- Obstacles ----
        update_obstacles(obstacles, vel, width, height)
        draw_obstacles(rgb, obstacles)

        # ---- BLUE BOOST ----
        blue_food = maybe_spawn_blue(blue_food, width, height)
        state["blue_food_pos"] = blue_food
        draw_blue_food(rgb, blue_food)

        if blue_food and dist(snake_pos, blue_food) < 20:
            state["speed_boost_active"] = True
            state["speed_boost_timer"] = time.time()
            state["blue_food_pos"] = None
            play_sound(SND_BOOST)

        if speed_boost_active and time.time() - state["speed_boost_timer"] > 7:
            state["speed_boost_active"] = False

        # ---- INVISIBLE POWER ----
        invisible_food = maybe_spawn_invisible(invisible_food, width, height)
        state["invisible_food_pos"] = invisible_food
        draw_invisible(rgb, invisible_food)

        if invisible_food and dist(snake_pos, invisible_food) < 20:
            state["invisible_active"] = True
            state["invisible_timer"] = time.time()
            state["invisible_food_pos"] = None
            play_sound(SND_BOOST)

        if invisible_active and time.time() - state["invisible_timer"] > 6:
            state["invisible_active"] = False

        # ---- FOOD COLLISION ----
        if dist(snake_pos, food_pos) < 20:
            if food_kind == "gold":
                score += 5
                play_sound(SND_EAT_GOLD)
            else:
                score += 1
                play_sound(SND_EAT_NORMAL)

            food_pos, food_kind = spawn_food(snake_body, width, height)

        draw_food(rgb, food_pos, food_kind, colors)

        # ---- BOSS FIGHT ----
        if level >= 10 and not state["boss_active"]:
            state["boss_active"] = True

        if state["boss_active"]:
            update_boss(state["boss_pos"], snake_pos)
            draw_boss(rgb, state["boss_pos"], colors)

            if boss_hits_snake(state["boss_pos"], snake_pos):
                game_over = True

        # ---- DRAW SNAKE ----
        draw_snake(rgb, snake_body, colors, particles)

        # ---- HUD ----
        now = time.time()
        r, g, b = int(128 + 127 * (now % 1)), 255, 255
        cv2.putText(rgb, f"Score: {score}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (r, g, b), 3)

        cv2.putText(rgb, f"High: {state['high_score']}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 215, 0), 2)

        level = 1 + score // 5
        state["level"] = level

        cv2.putText(rgb, f"Level: {level}", (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 200, 255), 2)

        # Level-up progress bar
        bar_w = int(((score % 5) / 5.0) * 200)
        cv2.rectangle(rgb, (20, 150), (220, 170), (40, 40, 40), -1)
        cv2.rectangle(rgb, (20, 150), (20 + bar_w, 170), (0, 200, 255), -1)

        # ---- COLLISIONS ----
        # border
        if snake_pos[0] < 5 or snake_pos[0] > width - 5 or snake_pos[1] < 5 or snake_pos[1] > height - 5:
            game_over = True

        # obstacles + self (unless invisible)
        if not state["invisible_active"]:
            for ox, oy, r in obstacles:
                if dist(snake_pos, [ox, oy]) < r + 10:
                    game_over = True

            if not game_over:
                for block in snake_body[4:]:
                    if dist(snake_pos, block) < 10:
                        game_over = True

        # Save state
        state["snake_pos"] = snake_pos
        state["snake_body"] = snake_body
        state["score"] = score
        state["food_pos"] = food_pos
        state["food_kind"] = food_kind
        state["game_over"] = game_over

    # -----------------------------------------------------------
    # GAME OVER SCREEN
    # -----------------------------------------------------------
    if state["game_over"]:

        # Update high score ONLY if beaten
        if state["score"] > state["high_score"]:
            state["high_score"] = state["score"]

        # Play sound only once
        if not state["game_over_sound_played"]:
            play_sound(SND_GAME_OVER)
            state["game_over_sound_played"] = True

        cv2.putText(rgb, "GAME OVER!", (width // 2 - 150, height // 2 - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 50, 50), 3)

        cv2.putText(rgb, "Show your hand to restart",
                    (width // 2 - 200, height // 2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # Restart when hand detected
        if results.multi_hand_landmarks:
            old_high = state["high_score"]
            new_state = init_state(width, height)
            new_state["high_score"] = old_high
            state.clear()
            state.update(new_state)

        return rgb, state, delay

    return rgb, state, delay
