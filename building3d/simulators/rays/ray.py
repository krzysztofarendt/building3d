from collections import deque

import numpy as np
import numba

from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.building import Building
from building3d.geom.solid import Solid
from building3d.geom.vector import length
from building3d.geom.paths.object_path import object_path
from building3d.geom.paths.object_path import split_path


@numba.njit
def reflect_ray(
    velocity: np.ndarray,
    surface_normal_vec: np.ndarray
) -> np.ndarray:
    dot = np.dot(surface_normal_vec, velocity)
    reflected = velocity - 2 * dot * surface_normal_vec
    return reflected


class Ray:
    buffer_size: int = 500  # how many past positions to remember

    def __init__(self, position: Point, building: Building, time_step: float):
        self.position = position
        self.building = building
        self.building_adj_polygons = building.get_graph()
        self.building_adj_solids = building.find_adjacent_solids()
        self.time_step = time_step
        self.speed = 0.0
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.past_positions = deque()
        for _ in range(Ray.buffer_size):
            self.past_positions.appendleft(self.position)

        self._target_surface: str = ""  # Path to polygon
        self._distance = None  # Distance to target surface
        self._prev_distance = 0.0
        self._distance_increment = 0.0
        self._location: str = ""  # Path to solid

    def update_target_surface(self):
        path_to_solid = self.get_location()
        zname, sname = split_path(path_to_solid)
        z = self.building.zones[zname]
        s = z.solids[sname]
        found = False

        for w in s.get_walls():
            for p in w.get_polygons():
                if p.is_point_inside_projection(self.position, self.velocity):
                    self.set_target_surface(object_path(zone=z, solid=s, wall=w, poly=p))
                    found = True
                    break
            if found:
                break

        if not found:
            # This should not happen, because all rays are initilized inside a solid
            # and solids must be fully enclosed with polygons
            raise RuntimeError("Some ray is not going towards any surface... (?)")

    def get_target_surface(self) -> str:
        return self._target_surface

    def set_target_surface(self, value: str):
        self._target_surface = value

    def update_location(self):
        """Update ray's location (solid name). Look only at current and adjacent solids."""
        curr_solid = self.get_location()
        adjacent_solids = self.building_adj_solids[curr_solid]
        adjacent_solids += [curr_solid]
        for path_to_solid in adjacent_solids:
            s = self.building.get_object(path_to_solid)
            if isinstance(s, Solid):
                if s.is_point_inside(self.position):
                    self.set_location(path_to_solid)
            else:
                raise TypeError(f"Incorrect solid type: {s}")

    def get_location(self) -> str:
        assert self._location != "", "Location uninitialized"
        return self._location

    def set_location(self, value: str):
        self._location = value

    def update_distance(self):
        # TODO: Use _distance_increment to speed up

        poly = self.building.get_object(self.get_target_surface())
        if not isinstance(poly, Polygon):
            raise TypeError(f"Incorrect polygon type: {type(poly)}")
        self.set_distance(poly.distance_point_to_polygon(self.position))

    def get_distance(self) -> None | float:
        return self._distance

    def set_distance(self, value: float):
        if self._distance is None or value > self._distance:
            # Bounced off a surface, new target surface assigned
            self._prev_distance = None
            self._distance = value
            self._distance_increment = None
        else:
            self._prev_distance = self._distance
            self._distance = value
            self._distance_increment = self._distance - self._prev_distance
        assert self._distance_increment is None or self._distance_increment <= 0, \
            f"Ray is moving away from the target surface? (dist_inc={self._distance_increment})"

    def get_distance_increment(self) -> None | float:
        return self._distance_increment

    def forward(self):
        """Run one time step forward and update the position."""
        # Update current position
        self.position += self.velocity * self.time_step

        # Add current position to buffer
        self.past_positions.appendleft(self.position)
        if len(self.past_positions) > Ray.buffer_size:
            _ = self.past_positions.pop()

    def set_speed(self, v: float) -> None:
        self.speed = v

    def set_direction(self, dx: float, dy: float, dz: float) -> None:
        assert self.speed != 0, "This check is just for debugging"  # TODO: Remove
        d = np.array([float(dx), float(dy), float(dz)])
        d /= length(d)
        d *= self.speed
        self.velocity = d

    def reflect(self, n: np.ndarray) -> None:
        """Bounce ray off a surface.

        Args:
            n: surface normal vector (should have unit length)
        """
        self.velocity = reflect_ray(self.velocity, n)
