from collections import deque
import logging

import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.polygon.distance import distance_point_to_polygon
from building3d.geom.numba.building import Building
from building3d.geom.numba.building.find_location import find_location
from building3d.geom.numba.vectors import normal, new_vector
from building3d.geom.paths import PATH_SEP
from building3d.geom.numba.types import PointType
from .find_transparent import find_transparent
from .find_target import find_target
from building3d.geom.paths.object_path import object_path, split_path
from building3d.simulators.rays.numba.find_transparent import find_transparent
from .get_property import get_property
from .config import RAY_LINE_LEN


logger = logging.getLogger(__name__)


class Ray:
    buff_size: int = RAY_LINE_LEN  # Used only for plotting
    transparent: set = set()
    transparent_checked = False

    speed: float = 343.0
    time_step: float = 0.0000625  # 62.5 ms, sampling rate = 16 kHz
    min_distance: float = speed * time_step * 1.1  # Cannot move closer the wall

    def __init__(
        self,
        position: PointType,
        building: Building,
        properties: None | dict = None,
    ):
        # Position
        self.pos = position
        # Building instance
        self.bdg = building
        # Velocity
        self.vel = new_vector(0.0, 0.0, 0.0)
        # Energy
        self.energy = 1.0

        # Current location (path to solid)
        self.loc: str = ""
        # Target surface path
        self.trg_surf: str = ""
        # Target surface absorption
        self.trg_absorption: float = 0.0

        # Distance to target surface (current, from last step, increment)
        self.dist = np.inf
        self.dist_prev = np.inf
        self.dist_inc = 0

        # Simulation step
        self.num_step = 0
        # Number of steps after touching last surface
        self.num_steps_after_contact = 0

        # If True, will stop this ray (end of simulation)
        self.stop = False

        # Wall properties
        if isinstance(properties, dict):
            self.prop = properties
        else:
            self.prop = Ray.default_properties(self.bdg)

        # Initialize buffer of previous positions
        self.past_pos = deque(maxlen=Ray.buff_size)
        for _ in range(Ray.buff_size):
            self.past_pos.appendleft(self.pos)

        # Find transparent surfaces
        if not Ray.transparent_checked:
            Ray.transparent = find_transparent(self.bdg)
            Ray.transparent_checked = True

        logger.debug(f"Ray created: {self}")

    @staticmethod
    def default_properties(building: Building):
        """Return default acoustic properties."""
        # Default values
        default_absorption = 0.1  # TODO: add to config

        # Fill in the property dict
        default = {"absorption": {}}

        for z in building.zones.keys():
            default["absorption"][z] = default_absorption

        return default

    def set_direction(self, dx: float, dy: float, dz: float) -> None:
        d = np.array([float(dx), float(dy), float(dz)])
        d /= np.linalg.norm(d)
        d *= Ray.speed
        self.vel = d

    def update_location(self) -> None:
        if self.energy <= 0:
            return

        logger.debug(f"Update location of {self}")

        # If target surface and/or last known solid are known, start searching with them
        # Otherwise search in unknown order
        first_look_at = []

        if len(self.loc) > 0:
            first_look_at.append(self.loc)

        if len(self.trg_surf) > 0:
            b, z, s, _, _ = split_path(self.trg_surf)
            trg_sld = PATH_SEP.join((b, z, s))
            first_look_at.append(trg_sld)

        self.loc = find_location(self.pos, self.bdg, *first_look_at)

        logger.debug(f"Update ray location to: {self.loc}")

    def update_target_surface(self) -> None:
        if self.energy <= 0:
            return

        logger.debug(f"Update target surface for {self}")
        self.trg_surf = find_target(
            pos=self.pos,
            vel=self.vel,
            loc=self.loc,
            bdg=self.bdg,
            trans=Ray.transparent,
            chk=set(),
        )
        self.target_absorption = get_property(
            self.trg_surf,
            "absorption",
            self.prop,
        )

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
        if self.trg_surf == "":
            return

        if self.energy <= 0:
            return

        if fast_calc:
            # This method should be called only when far enough from the target surface
            self.dist_prev = self.dist
            self.dist += self.dist_inc
        else:
            # TODO: This used to be very slow. Can it be faster?
            logger.debug(f"Accurate distance calculation for {self}")
            poly = self.bdg.get(self.trg_surf)
            assert isinstance(poly, Polygon)

            self.dist_prev = self.dist
            self.dist = distance_point_to_polygon(self.pos, poly.pts, poly.tri, poly.vn)
            self.dist_inc = self.dist - self.dist_prev
            logger.debug(f"{self.dist=}, {self.dist_prev=}, {self.dist_inc=}")

    def forward(self) -> None:
        """Run one step forward and update the position."""
        if self.energy <= 0:
            return

        # If distance below threshold, reflect (change direction)
        max_allowed_lags = 10

        if self.num_step == 0:
            assert len(self.loc) > 0, "Ray initial location not set"
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

                assert self.trg_surf not in Ray.transparent

                # Reflect
                poly = self.bdg.get(self.trg_surf)
                assert isinstance(poly, Polygon)
                self.reflect(poly.vn)
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
                        f"{self} is too close to the surface {self.trg_surf} to move forward."
                    )
                    # Remember that this ray is 1 step behind due to corner reflection
                    # The lag has to be reduced by moving forward multiple times once
                    # the target surface which is far enough is found
                    lag += 1
                    continue

                if lag >= max_allowed_lags:
                    raise RuntimeError("Too many reflections caused too high ray lag.")

            # Move forward
            self.pos += self.vel * Ray.time_step
            fast_calc = True if self.num_steps_after_contact > 1 else False
            self.update_distance(fast_calc)
            lag -= 1

            # Add current position to buffer
            self.past_pos.appendleft(self.pos)
            if len(self.past_pos) > Ray.buff_size:
                _ = self.past_pos.pop()

            self.num_step += 1

        self.num_steps_after_contact += 1

    def reflect(self, vn: np.ndarray) -> None:
        """Bounce ray off a surface.

        Args:
            vn: surface normal vector (should have unit length)
        """
        logger.debug(f"Reflect: {self}")
        speed_before = np.linalg.norm(self.vel)

        dot = np.dot(vn, self.vel)
        self.vel = self.vel - 2 * dot * vn

        speed_after = np.linalg.norm(self.vel)
        assert np.isclose(speed_before, speed_after)

        # Absorp part of the ray energy
        self.energy -= self.target_absorption

        if self.energy <= 0:
            logger.debug(f"Ray stopped, energy=0: {self}")
            self.vel = np.array([0.0, 0.0, 0.0])
            self.energy = 0.0
