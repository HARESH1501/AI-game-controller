import cv2

def move_snake(snake_pos, target_x, target_y, smoothing):
    snake_pos[0] += (target_x - snake_pos[0]) * smoothing
    snake_pos[1] += (target_y - snake_pos[1]) * smoothing

def update_body(snake_body, snake_pos, score):
    snake_body.insert(0, list(snake_pos))
    if len(snake_body) > score + 3:
        snake_body.pop()

def draw_snake(rgb, snake_body, colors, particle_list):
    # particles from head
    if snake_body:
        head = snake_body[0]
        particle_list.append([head[0], head[1], 15])

    # draw particles
    for p in particle_list[:]:
        px, py, pr = p
        cv2.circle(rgb, (int(px), int(py)), pr, colors["particle"], 1)
        p[2] -= 1
        if p[2] <= 0:
            particle_list.remove(p)

    # draw snake body
    for i, block in enumerate(snake_body):
        cv2.circle(rgb, (int(block[0]), int(block[1])), 15, colors["snake_body"], 2)
        col = colors["snake_head"] if i == 0 else colors["snake_body"]
        cv2.circle(rgb, (int(block[0]), int(block[1])), 10, col, -1)
