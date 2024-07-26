from collections import deque
import logging

import numpy as np

from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.building import Building
from building3d.geom.vector import length
from building3d.geom.paths import PATH_SEP
from .find_location import find_location
from .find_target import find_target
from .find_transparent import find_transparent
from .get_property import get_property


logger = logging.getLogger(__name__)


class Ray:
    buffer_size: int = 10  # how many past positions to remember, used only for plotting
    transparent = []
    transparent_checked = False

    speed: float = 343.0
    time_step: float = 1e-4
    min_distance: float = speed * time_step * 1.1  # Cannot move closer the wall

    def __init__(
        self,
        position: Point,
        building: Building,
        properties: None | dict = None,
    ):
        self.position = position
        self.building = building

        if isinstance(properties, dict):
            self.properties = properties
        else:
            self.properties = Ray.default_properties(building)

        self.velocity = np.array([0.0, 0.0, 0.0])
        self.energy = 1.0

        if not Ray.transparent_checked:
            Ray.transparent = find_transparent(building)

        self.past_positions = deque()
        for _ in range(Ray.buffer_size):
            self.past_positions.appendleft(self.position)

        self.location: str = ""
        self.target_surface: str = ""
        self.target_absorption: float = 0.0

        self.dist = np.inf
        self.dist_prev = np.inf
        self.dist_inc = 0
        self.num_step = 0
        self.num_steps_after_contact = 0
        self.stop = False

        logger.debug(f"Ray created: {self}")

    @staticmethod
    def default_properties(building: Building):
        """Return default acoustic properties."""
        # Default values
        default_absorption = 0.1

        # Fill in the property dict
        default = {"absorption": {}}

        for z in building.get_zone_names():
            default["absorption"][z] = default_absorption

        return default

    def update_location(self):
        if self.energy <= 0:
            return

        logger.debug(f"Update location of: {self}")
        try:
            # If target surface and/or last known solid are known, start searching with them
            # Otherwise search in unknown order
            if len(self.target_surface) > 0 and len(self.location) > 0:
                z, s, _, _ = self.target_surface.split(PATH_SEP)
                target_solid = z + PATH_SEP + s
                self.location = find_location(self.position, self.building, target_solid, self.location)
            elif len(self.location) > 0:
                self.location = find_location(self.position, self.building, self.location)
            else:
                self.location = find_location(self.position, self.building)

        except RuntimeError as e:
            logging.error(str(e))
            logging.error(f"Affected ray: {self}")
            logging.info(f"Past ray positions: {self.past_positions}")
            logging.shutdown()
            raise e

        logger.debug(f"Update ray location to: {self.location}")

    def update_target_surface(self):
        if self.energy <= 0:
            return

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
            self.target_absorption = get_property(
                self.target_surface,
                "absorption",
                self.properties,
            )
        except RuntimeError as e:
            logging.error(str(e))
            logging.error(f"Affected ray: {self}")
            logging.shutdown()
            raise e

    def update_distance(self, fast_calc: bool) -> None:
        """Update distance to the target surface.

        This function is sped up by avoiding recalculating the distance
        at each step. The ray moves along straight lines and the surrounding
        geometry does not change, so we can cache the distance increments.

        The actual distance calculation must take place only after reflection.

        Args:
            fast_calc: whether to use use fast calculation method or the accurate one

        Return:
            None
        """
        if self.energy <= 0:
            return

        if fast_calc:
            # This method should be called only when far enough from the target surface
            self.dist_prev = self.dist
            self.dist += self.dist_inc
        else:
            # TODO: This is very slow. Can it be faster?
            logger.debug(f"Accurate distance calculation for {self}")
            poly = self.building.get_object(self.target_surface)
            assert isinstance(poly, Polygon)
            self.dist_prev = self.dist
            self.dist = poly.distance_point_to_polygon(self.position)
            self.dist_inc = self.dist - self.dist_prev
            logger.debug(f"{self.dist=}, {self.dist_prev=}, {self.dist_inc=}")

    def forward(self) -> None:
        """Run one step forward and update the position."""
        if self.energy <= 0:
            return

        # If distance below threshold, reflect (change direction)
        max_allowed_lags = 10

        if self.num_step == 0:
            assert len(self.location) > 0, "Ray initial location not set"
            self.update_target_surface()
            self.update_distance(fast_calc=False)

        # Schedule at least 1 step forward
        lag = 1

        # Move forward until lag is reduced to 0
        # (there may be additional lag when the ray is reflected near a corner
        #  and can't immediately move, because it would go outside the building)
        while lag > 0:
            if self.dist <= Ray.min_distance:
                logger.debug(f"Ray needs to be reflected: {self}")

                assert self.target_surface not in Ray.transparent

                # Reflect
                poly = self.building.get_object(self.target_surface)
                assert isinstance(poly, Polygon)
                self.reflect(poly.normal)
                if self.energy <= 0:
                    break
                self.update_location()
                self.update_target_surface()
                self.num_steps_after_contact = 0
                self.update_distance(fast_calc=False)

                # Check if can move forward in the next step
                # (if the next target surface is not too close)
                if self.dist <= Ray.min_distance:
                    logger.debug(
                        f"{self} is too close to the surface {self.target_surface} to move forward."
                    )
                    # Remember that this ray is 1 step behind due to corner reflection
                    # The lag has to be reduced by moving forward multiple times once
                    # the target surface which is far enough is found
                    lag += 1
                    continue

                if lag >= max_allowed_lags:
                    raise RuntimeError("Too many reflections caused too high ray lag.")

            # Move forward
            self.position += self.velocity * Ray.time_step
            fast_calc = True if self.num_steps_after_contact > 1 else False
            self.update_distance(fast_calc)
            lag -= 1

            # Add current position to buffer
            self.past_positions.appendleft(self.position)
            if len(self.past_positions) > Ray.buffer_size:
                _ = self.past_positions.pop()

            self.num_step += 1

        self.num_steps_after_contact += 1

    def set_direction(self, dx: float, dy: float, dz: float) -> None:
        d = np.array([float(dx), float(dy), float(dz)])
        d /= length(d)
        d *= Ray.speed
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

        # Absorp part of the ray energy
        self.energy -= self.target_absorption

        if self.energy <= 0:
            logger.debug(f"Ray stopped, energy=0: {self}")
            self.velocity = np.array([0.0, 0.0, 0.0])
            self.energy = 0.0

    def __str__(self):
        s = "Ray("
        s += f"id={hex(id(self))}, "
        s += f"pos={self.position}, "
        s += f"enr={self.energy:.2f}, "
        s += f"loc={self.location}, "
        s += f"trg={self.target_surface}, "
        s += f"dst={self.dist:.3f}, "
        s += f"inc={self.dist_inc:.3f}, "
        s += f"vel={self.velocity*Ray.time_step}"
        s += "}"
        return s

    def __repr__(self):
        return self.__str__()
