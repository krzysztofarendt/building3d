from collections import deque

import numpy as np

from building3d.geom.point import Point
from building3d.geom.vector import length


class Ray:
    buffer_size: int = 3  # how many past positions to remember

    def __init__(self, position: Point):
        self.position = position
        self.velocity = 0.0
        self.direction = np.array([0.0, 0.0, 0.0])
        self.past_positions = deque()
        for _ in range(Ray.buffer_size):
            self.past_positions.appendleft(self.position)

    def forward(self):
        """Run one time step forward and update the position."""
        # Update current position
        self.position += self.direction

        # Add current position to buffer
        self.past_positions.appendleft(self.position)
        if len(self.past_positions) > Ray.buffer_size:
            _ = self.past_positions.pop()

        # TODO: Add collision detection, but WHERE? Probably not here

    def set_velocity(self, v: float) -> None:
        self.velocity = v

    def set_direction(self, dx: float, dy: float, dz: float) -> None:
        assert self.velocity != 0, "This check is just for debugging"  # TODO: Remove
        d = np.array([float(dx), float(dy), float(dz)])
        d /= length(d)
        d *= self.velocity
        self.direction = d


class RayCluster:
    def __init__(self, rays: list[Ray]):
        assert len(rays) > 0, "No rays provided to RayCluster.__init__()"
        self.rays = rays

    def forward(self):
        """Run one time step forward and update the position of all rays."""
        for r in self.rays:
            r.forward()

    def get_lines(self) -> tuple[list[Point], list[list[int]]]:
        line_len = Ray.buffer_size

        verts = []
        lines = []
        curr_index = 0
        for r in self.rays:
            verts.extend(list(r.past_positions))
            lines.append([curr_index + i for i in range(line_len)])
            curr_index += line_len

        return verts, lines

    def get_points(self) -> list[Point]:
        return [r.position for r in self.rays]
