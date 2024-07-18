from building3d import random_between
from building3d.geom.point import Point
from building3d.geom.building import Building
from building3d.geom.paths.object_path import object_path
from .ray import Ray


class ManyRays:
    """Collection of `Ray` instances located in a `Building`."""
    def __init__(
            self,
            source: Point,
            building: Building,
            speed: float = 343.0,
            time_step: float = 1e-4,
    ):
        self.source = source
        self.building = building
        self.building_adj_polygons = building.get_graph()
        self.building_adj_solids = building.find_adjacent_solids()
        self.speed = speed
        self.time_step = time_step
        self.rays: list[Ray] = []

    def add_rays(self, num_rays: int):
        for _ in range(num_rays):
            r = Ray(
                position=self.source,
                building=self.building,
                speed=self.speed,
                time_step=self.time_step,
            )
            r.set_direction(
                dx = random_between(-1, 1),  # TODO: direction within xlim possible
                dy = random_between(-1, 1),  # TODO: direction within ylim possible
                dz = random_between(-1, 1),  # TODO: direction within zlim possible
            )
            self.rays.append(r)

    def init_location(self):
        """Initialize the location for all rays based on the source's position."""
        if self.source is None:
            raise TypeError("Source is uninitialized?")
        path_to_solid = ""
        for z in self.building.get_zones():
            for s in z.get_solids():
                if s.is_point_inside(self.source):
                    path_to_solid = object_path(zone=z, solid=s)
                    self.set_locations(path_to_solid)

    def set_locations(self, value: str):
        for i in range(len(self.rays)):
            self.rays[i].location = value

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