from collections import deque
import logging

import numpy as np

from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.building import Building
from building3d.geom.vector import length
from building3d.geom.paths import PATH_SEP
from .get_location import get_location
from .find_target import find_target
from .find_transparent import find_transparent


logger = logging.getLogger(__name__)


class Ray:
    buffer_size: int = 500  # how many past positions to remember
    transparent = []
    transparent_checked = False

    def __init__(
            self,
            position: Point,
            building: Building,
            speed: float = 343.0,
            time_step: float = 1e-4,
    ):
        self.position = position
        self.building = building

        self.time_step = time_step
        self.speed = speed
        self.velocity = np.array([0.0, 0.0, 0.0])

        if not Ray.transparent_checked:
            Ray.transparent = find_transparent(building)

        self.past_positions = deque()
        for _ in range(Ray.buffer_size):
            self.past_positions.appendleft(self.position)

        self.location: str = ""
        self.target_surface: str = ""

        self.dist = np.inf
        self.dist_prev = np.inf
        self.dist_inc = 0
        self.num_steps_after_contact = 0
        self.stop = False

        logger.debug(f"Ray created: {self}")

    def update_location(self):
        logger.debug(f"Update location of: {self}")
        try:

            z, s, _, _ = self.target_surface.split(PATH_SEP)
            target_solid = z + PATH_SEP + s

            assert len(target_solid) > 0
            assert len(self.location) > 0

            self.location = get_location(self.position, self.building, target_solid, self.location)

        except RuntimeError as e:
            logging.error(str(e))
            logging.error(f"Affected ray: {self}")
            logging.shutdown()
            raise e

        logger.debug(f"Update ray location to: {self.location}")

    def update_target_surface(self):
        logger.debug(f"Update target surface for {self}")
        try:
            self.target_surface = find_target(
                position = self.position,
                velocity = self.velocity,
                location = self.location,
                building = self.building,
                transparent = Ray.transparent,
                checked_locations = set(),
            )
        except RuntimeError as e:
            logging.error(str(e))
            logging.error(f"Affected ray: {self}")
            logging.shutdown()
            raise e

    def update_distance(self):
        """Update distance to the target surface.

        This function is sped up by avoiding recalculating the distance
        at each step. The ray moves along straight lines and the surrounding
        geometry does not change, so we can cache the distance increments.

        The actual distance calculation must take place only after:
        - reflection
        - passing through a transparent surface (!!!TODO!!!)
        """
        fast_calc = False
        if self.num_steps_after_contact > 1:
            fast_calc = True

        if fast_calc:
            self.dist_prev = self.dist
            self.dist += self.dist_inc
            # NOTE: After reflection nead an edge/corner, ray may go outside building!
            #       Currently it is taken care of in RaySimulator.forward()
        else:
            logger.debug(f"Accurate distance calculation for {self}")
            poly = self.building.get_object(self.target_surface)
            assert isinstance(poly, Polygon)
            self.dist_prev = self.dist
            self.dist = poly.distance_point_to_polygon(self.position)
            self.dist_inc = self.dist - self.dist_prev
            logger.debug(f"{self.dist=}, {self.dist_prev=}, {self.dist_inc=}")

    def forward(self):
        """Run one step forward and update the position."""
        # Update current position
        self.position += self.velocity * self.time_step
        self.update_distance()
        self.num_steps_after_contact += 1

        # Add current position to buffer
        self.past_positions.appendleft(self.position)
        if len(self.past_positions) > Ray.buffer_size:
            _ = self.past_positions.pop()

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
        logger.debug(f"Reflect: {self}")
        speed_before = length(self.velocity)
        dot = np.dot(n, self.velocity)
        self.velocity = self.velocity - 2 * dot * n
        speed_after = length(self.velocity)
        assert np.isclose(speed_before, speed_after)
        self.num_steps_after_contact = 0

    def __str__(self):
        s = "Ray("
        s += f"pos={self.position}, "
        s += f"loc={self.location}, "
        s += f"trg={self.target_surface}, "
        s += f"dst={self.dist:.3f}, "
        s += f"inc={self.dist_inc:.3f}, "
        s += f"vel={self.velocity*self.time_step})"
        return s

    def __repr__(self):
        return self.__str__()
