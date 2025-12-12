import math
import random

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def random_pos(width, height, margin=20):
    return (
        random.randint(margin, width - margin),
        random.randint(margin, height - margin),
    )
