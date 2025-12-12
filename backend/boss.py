import cv2
from .utils import dist

def update_boss(boss_pos, snake_pos):
    boss_pos[0] += (snake_pos[0] - boss_pos[0]) * 0.01
    boss_pos[1] += (snake_pos[1] - boss_pos[1]) * 0.01

def draw_boss(rgb, boss_pos, colors):
    cv2.circle(rgb, (int(boss_pos[0]), int(boss_pos[1])), 60, colors["boss"], -1)
    cv2.circle(rgb, (int(boss_pos[0]), int(boss_pos[1])), 80, colors["boss"], 3)

def boss_hits_snake(boss_pos, snake_pos, threshold=70):
    return dist(boss_pos, snake_pos) < threshold
