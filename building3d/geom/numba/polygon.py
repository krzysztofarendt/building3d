import numpy as np
from numpy.typing import NDArray
from numba import njit

from building3d import random_id
from building3d.geom.paths.validate_name import validate_name


class Polygon:
    def __init__(
        self,
        points: NDArray[np.float32],
        name: str | None = None,
        uid: str | None = None,
    ):
        if name is None:
            name = random_id()
        self.name = validate_name(name)

        if uid is None:
            self.uid = random_id()
        else:
            self.uid = uid

        self.points = points
        self.triangles: NDArray[np.int32] = np.array([])
