from building3d import random_between
from building3d.geom.point import Point
from .ray import Ray


class ManyRays:
    """Collection of `Ray` instances.

    This class holds a collection of rays.
    It has methods for:
    - creating new rays at a given source
    - moving forward with the simulation
    - returning geometry for plotting with `plot_objects()`

    `ManyRays` doesn't know anything about surrounding objects.
    The information about the surrounding obstacles is defined in `RaySimulator`.
    """
    def __init__(self, speed: float, time_step: float):
        self.speed = speed
        self.time_step = time_step
        self.rays = []

    def add_rays(self, source: Point, num_rays: int):
        for _ in range(num_rays):
            r = Ray(source, self.time_step)
            r.set_speed(self.speed)
            r.set_direction(
                dx = random_between(-1, 1),  # TODO: direction within xlim possible
                dy = random_between(-1, 1),  # TODO: direction within ylim possible
                dz = random_between(-1, 1),  # TODO: direction within zlim possible
            )
            self.rays.append(r)

    def forward(self):
        """Run one time step forward and update the position of all rays."""
        for r in self.rays:
            r.forward()

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
