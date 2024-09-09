from collections import deque
import logging

import numpy as np

from building3d.geom.polygon import Polygon
from building3d.geom.polygon.distance import distance_point_to_polygon
from building3d.geom.building import Building
from building3d.geom.building.find_location import find_location
from building3d.geom.vectors import new_vector
from building3d.geom.paths import PATH_SEP
from building3d.geom.types import PointType
from .find_target import find_target
from building3d.geom.paths.object_path import split_path
from building3d.simulators.rays.find_transparent import find_transparent
from .properties import default_properties, get_property
from .config import RAY_LINE_LEN
from building3d.config import EPSILON


logger = logging.getLogger(__name__)


class Ray:
    buff_size: int = RAY_LINE_LEN  # Used only for plotting
    speed: float = 343.0
    time_step: float = 0.00003125  # 31.25 ms, sampling rate = 32 kHz
    min_dist: float = speed * time_step * 2.0  # Cannot move closer the wall

    def __init__(
        self,
        position: PointType,
        building: Building,
        properties: None | dict = None,
    ):
        # Position
        self.pos = position.copy()
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
        self.dist_inc = 0.0

        # Number of steps after touching last surface
        self.num_steps_after_contact = 0

        # If True, will stop this ray (end of simulation)
        self.stop = False

        # Wall properties
        if isinstance(properties, dict):
            self.prop = properties
        else:
            self.prop = default_properties(self.bdg)

        # Initialize buffer of previous positions
        self.past_pos = deque(maxlen=Ray.buff_size)
        for _ in range(Ray.buff_size):
            self.past_pos.appendleft(self.pos.copy())

        # Find transparent surfaces
        self.transparent = find_transparent(self.bdg)

        logger.debug(f"Ray created: {self}")

    def set_direction(self, dx: float, dy: float, dz: float) -> None:
        d = np.array([float(dx), float(dy), float(dz)])
        d /= np.linalg.norm(d)
        self.vel = d * Ray.speed * Ray.time_step

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
            trans=self.transparent,
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

        if (fast_calc and self.dist_inc < 0 and not np.isinf(self.dist_inc)):
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

            if np.isinf(self.dist_inc) or np.abs(self.dist_inc) >= Ray.min_dist:
                self.dist_inc = 0.0

            # Sanity check
            assert np.abs(self.dist_inc) < Ray.min_dist, \
                f"{np.abs(self.dist_inc)=}, {Ray.min_dist=}"

            logger.debug(f"{self.dist=}, {self.dist_prev=}, {self.dist_inc=}")

    def forward(self) -> None:
        """Run one step forward and update the position."""
        if self.energy <= 0:
            return

        # self.update_distance(fast_calc=False)
        if self.trg_surf == "":
            self.update_target_surface()
        if np.isinf(self.dist):
            self.update_distance(fast_calc=False)

        # Ensure accurate distance calculation when close to surfaces to prevent ray escape
        if self.dist <= Ray.min_dist:
            self.update_distance(fast_calc=False)

        # If distance below threshold, reflect (change direction)
        max_allowed_lags = 10

        # Schedule at least 1 step forward
        lag = 1

        # Move forward until lag is reduced to 0
        # (there may be additional lag when the ray is reflected near a corner
        #  and can't immediately move, because it would go outside the building)
        while lag > 0:
            if self.dist <= Ray.min_dist:
                logger.debug(f"Ray needs to be reflected: {self}")

                assert self.trg_surf not in self.transparent

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
                if self.dist <= Ray.min_dist:
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
            assert (np.abs(self.vel * Ray.time_step) < Ray.min_dist).all()  # Sanity check
            self.pos += self.vel
            lag -= 1

            # Update distance
            if self.num_steps_after_contact > 1 and self.dist > Ray.min_dist:
                fast_calc = True
            else:
                fast_calc = False
            self.update_distance(fast_calc=fast_calc)

            # Add current position to buffer
            self.past_pos.appendleft(self.pos.copy())
            if len(self.past_pos) > Ray.buff_size:
                _ = self.past_pos.pop()

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
            self.trg_surf = ""

    def __str__(self):
        s = "Ray("
        s += f"id={hex(id(self))}, "
        s += f"pos={self.pos}, "
        s += f"enr={self.energy:.2f}, "
        s += f"loc={self.loc}, "
        s += f"trg={self.trg_surf}, "
        s += f"dst={self.dist:.3f}, "
        s += f"inc={self.dist_inc:.3f}, "
        s += f"vel={self.vel*Ray.time_step}"
        s += "}"
        return s

    def __repr__(self):
        return self.__str__()
