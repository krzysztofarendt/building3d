from collections import deque

import numpy as np
import numba

from building3d.geom.point import Point
from building3d.geom.vector import length


@numba.njit
def reflect_ray(
    velocity: np.ndarray,
    surface_normal_vec: np.ndarray
) -> np.ndarray:
    dot = np.dot(surface_normal_vec, velocity)
    reflected = velocity - 2 * dot * surface_normal_vec
    return reflected


class Ray:
    buffer_size: int = 500  # how many past positions to remember

    def __init__(self, position: Point, time_step: float):
        self.position = position
        self.time_step = time_step
        self.speed = 0.0
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.past_positions = deque()
        for _ in range(Ray.buffer_size):
            self.past_positions.appendleft(self.position)

        self.next_surf = ""

    @property
    def next_surface(self):
        return self.next_surf

    @next_surface.setter
    def next_surface(self, value):
        self.next_surf = value

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

    def reflect(self, n: np.ndarray) -> None:
        """Bounce ray off a surface.

        Args:
            n: surface normal vector (should have unit length)
        """
        self.velocity = reflect_ray(self.velocity, n)
