from collections import deque

import numpy as np

from building3d.geom.point import Point
from building3d.geom.vector import length


class Ray:
    buffer_size: int = 10  # how many past positions to remember

    def __init__(self, position: Point, time_step: float = 1e-3):
        self.position = position
        self.time_step = time_step
        self.speed = 0.0
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.past_positions = deque()
        for _ in range(Ray.buffer_size):
            self.past_positions.appendleft(self.position)

    def forward(self):
        """Run one time step forward and update the position."""
        # Update current position
        self.position += self.velocity * self.time_step

        # Add current position to buffer
        self.past_positions.appendleft(self.position)
        if len(self.past_positions) > Ray.buffer_size:
            _ = self.past_positions.pop()

    def set_speed(self, v: float) -> None:
        self.speed = v

    def set_direction(self, dx: float, dy: float, dz: float) -> None:
        assert self.speed != 0, "This check is just for debugging"  # TODO: Remove
        d = np.array([float(dx), float(dy), float(dz)])
        d /= length(d)
        d *= self.speed
        self.velocity = d
