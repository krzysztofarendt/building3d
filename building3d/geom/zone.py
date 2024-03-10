import numpy as np

from .wall import Wall
from .solid import Solid


class Zone(Solid):
    def __init__(self, name: str, walls: list[Wall]):
        super().__init__(walls)
        self.name = name
        self.walls = self.boundary
