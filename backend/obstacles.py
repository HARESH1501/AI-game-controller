import cv2

def update_obstacles(obstacles, velocities, width, height):

    for i, obs in enumerate(obstacles):
        ox, oy, r = obs
        vx, vy = velocities[i]

        ox += vx
        oy += vy

        if ox < r or ox > width - r:
            vx *= -1
        if oy < r or oy > height - r:
            vy *= -1

        obstacles[i] = [ox, oy, r]
        velocities[i] = [vx, vy]


def draw_obstacles(rgb, obstacles):
    for ox, oy, r in obstacles:
        cv2.circle(rgb, (int(ox), int(oy)), r, (140, 140, 140), -1)
