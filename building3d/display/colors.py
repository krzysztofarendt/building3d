import numpy as np


RGB_WHITE = (1, 1, 1)
RGB_RED = (1, 0, 0)
RGB_BLUE = (0, 0, 1)
RGB_GREEN = (0, 1, 0)


def random_color():
    return tuple(np.random.random(3))
