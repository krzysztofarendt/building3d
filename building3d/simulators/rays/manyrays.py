import logging

from building3d import random_between
from building3d.geom.point import Point
from building3d.geom.building import Building
from building3d.geom.paths.object_path import object_path
from .ray import Ray
from .get_location import get_location


logger = logging.getLogger(__name__)


class ManyRays:
    """Collection of `Ray` instances located in a `Building`."""
    def __init__(
        self,
        num_rays: int,
        source: Point,
        building: Building,
        speed: float = 343.0,
        time_step: float = 1e-4,
    ):
        logger.debug("ManyRays initialization")

        self.num_rays = num_rays
        self.source = source
        self.rays: list[Ray] = []

        init_loc = get_location(p=source, building=building)

        # Set omnidirectional source
        for _ in range(num_rays):
            r = Ray(
                position=source,
                building=building,
                speed=speed,
                time_step=time_step,
            )
            r.location = init_loc
            r.set_direction(
                dx = random_between(-1, 1),  # TODO: direction within xlim possible
                dy = random_between(-1, 1),  # TODO: direction within ylim possible
                dz = random_between(-1, 1),  # TODO: direction within zlim possible
            )
            self.rays.append(r)

    def get_lines(self) -> tuple[list[Point], list[list[int]]]:
        """Interface to building3d.display.plot_objects.plot_objects()"""
        line_len = Ray.buffer_size

        verts = []
        lines = []
        curr_index = 0
        for r in self.rays:
            verts.extend(list(r.past_positions))
            lines.append([curr_index + i for i in range(line_len)])
            curr_index += line_len

        return verts, lines

    def get_points(self) -> list[Point]:
        """Interface to building3d.display.plot_objects.plot_objects()"""
        return [r.position for r in self.rays]

    def __len__(self):
        return len(self.rays)

    def __getitem__(self, key: int) -> Ray:
        if not isinstance(key, int):
            raise TypeError(f"Incorrect key type: {type(key)} (should be int)")
        return self.rays[key]

    def __setitem__(self, key: int, value: Ray) -> None:
        if not isinstance(key, int):
            raise TypeError(f"Incorrect key type: {type(key)} (should be int)")
        if not isinstance(value, Ray):
            raise TypeError(f"Incorrect value type: {type(key)} (should be Ray)")
        self.rays[key] = value

    def __str__(self):
        s = f"ManyRays(num_rays={self.num_rays}, source={self.source}, id={hex(id(self))})"
        return s
