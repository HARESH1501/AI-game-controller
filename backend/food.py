import cv2
import random
from .utils import dist, random_pos

def spawn_food(snake_body, width, height):
    while True:
        x, y = random_pos(width, height)
        if all(dist([x, y], block) > 25 for block in snake_body):
            kind = "gold" if random.random() < 0.2 else "normal"
            return [x, y], kind

def draw_food(rgb, food_pos, food_kind, colors):
    col = colors["food_gold"] if food_kind == "gold" else colors["food_normal"]
    cv2.circle(rgb, (int(food_pos[0]), int(food_pos[1])), 10, col, -1)

def maybe_spawn_blue(blue_food_pos, width, height):
    if blue_food_pos is None and random.random() < 0.01:
        x, y = random_pos(width, height)
        return [x, y]
    return blue_food_pos

def draw_blue_food(rgb, blue_food_pos):
    if blue_food_pos:
        cv2.circle(rgb, (int(blue_food_pos[0]), int(blue_food_pos[1])),
                   10, (0, 128, 255), -1)

def maybe_spawn_invisible(invisible_pos, width, height):
    if invisible_pos is None and random.random() < 0.005:
        x, y = random_pos(width, height)
        return [x, y]
    return invisible_pos

def draw_invisible(rgb, invisible_pos):
    if invisible_pos:
        cv2.circle(rgb, (int(invisible_pos[0]), int(invisible_pos[1])),
                   10, (255, 255, 255), 2)
