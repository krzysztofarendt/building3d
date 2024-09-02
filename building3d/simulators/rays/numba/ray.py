from collections import deque
import logging

import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.building import Building
from building3d.geom.numba.building.find_location import find_location
from building3d.geom.numba.vectors import normal, new_vector
from building3d.geom.paths import PATH_SEP
from building3d.geom.numba.types import PointType
from .find_transparent import find_transparent
from .find_target import find_target
from building3d.geom.paths.object_path import object_path, split_path
from building3d.simulators.rays.numba.find_transparent import find_transparent
# from .get_property import get_property
from .config import RAY_LINE_LEN


logger = logging.getLogger(__name__)


class Ray:
    buff_size: int = RAY_LINE_LEN  # Used only for plotting
    transparent = []
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
        self.enr = 1.0

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
        default_absorption = 0.1

        # Fill in the property dict
        default = {"absorption": {}}

        for z in building.zones.keys():
            default["absorption"][z] = default_absorption

        return default

    def update_location(self):
        if self.enr <= 0:
            return

        logger.debug(f"Update location of {self}")

        # If target surface and/or last known solid are known, start searching with them
        # Otherwise search in unknown order
        first_look_at = []

        if len(self.loc) > 0:
            first_look_at.append(self.loc)

        if len(self.trg_surf) > 0:
            z, s, _, _ = split_path(self.trg_surf)
            trg_sld = object_path(zone=z, solid=s)
            first_look_at.append(trg_sld)

        self.loc = find_location(self.pos, self.bdg, *first_look_at)

        logger.debug(f"Update ray location to: {self.loc}")
