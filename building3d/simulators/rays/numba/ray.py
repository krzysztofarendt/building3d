from collections import deque
import logging

import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.building import Building
from building3d.geom.numba.vectors import normal, new_vector
from building3d.geom.paths import PATH_SEP
from building3d.geom.numba.types import PointType
from .find_transparent import find_transparent
# from .find_target import find_target
# from .find_transparent import find_transparent
# from .get_property import get_property
from .config import RAY_LINE_LEN


logger = logging.getLogger(__name__)


class Ray:
    buffer_size: int = RAY_LINE_LEN  # Used only for plotting
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
        self.pos = position
        self.bdg = building

        if isinstance(properties, dict):
            self.prop = properties
        else:
            self.prop = Ray.default_properties(self.bdg)

        self.vel = new_vector(0.0, 0.0, 0.0)
        self.enr = 1.0

        if not Ray.transparent_checked:
            Ray.transparent = find_transparent(self.bdg)

        ...

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

