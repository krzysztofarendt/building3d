"""Zone class"""

from .wall import Wall
from .solid import Solid


class Zone(Solid):
    """Zone is a subclass of Solid with additional attributes and methods."""

    def __init__(self, name: str, walls: list[Wall]):
        super().__init__(name, walls)
        self.walls = walls

    def __str__(self):
        s =  f"Zone(name={self.name},\n"
        for w in self.walls:
            s += f"     {w}\n"
        s += f") -> volume={self.volume:.3f}\n"
        return s
