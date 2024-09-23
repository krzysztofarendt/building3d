from numba import njit
import numpy as np

from building3d.io.arrayformat import to_array_format
from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.polygon import Polygon
from building3d.geom.polygon.ispointinside import is_point_inside_projection
from building3d.geom.types import PointType, VectorType, IndexType, IntDataType, FLOAT, INT
from building3d.display.plot_objects import plot_objects
from .find_transparent import find_transparent


class RayPlotter:
    def __init__(self, points):
        self.points = points

    def get_points(self):
        return self.points


class Simulation:

    def __init__(
        self,
        building: Building,
        source: PointType,
        sinks: PointType,
        num_rays: int,
        num_steps: int,
    ):
        self.building = building
        self.source = source.copy()
        self.sinks = sinks.copy()
        self.num_rays = num_rays
        self.num_steps = num_steps

    def run(self):
        # Get transparent polygons
        trans_poly_paths = find_transparent(self.building)
        trans_poly_nums = set()
        for poly_path in trans_poly_paths:
            poly = self.building.get(poly_path)
            assert isinstance(poly, Polygon)
            trans_poly_nums.add(poly.num)

        # Convert building to the array format
        points, faces, polygons, walls, solids, zones = to_array_format(self.building)

        # Run simulation loop (JIT compiled)
        ray_pos, hits = simulation_loop(
            self.num_steps,
            self.num_rays,
            source = self.source,
            sinks = self.sinks,
            points = points,
            faces = faces,
            polygons = polygons,
            walls = walls,
            solids = solids,
            zones = zones,
            trans_poly_nums = trans_poly_nums,
        )
        ray_plotter = RayPlotter(ray_pos)
        colors = ([1.0, 1.0, 1.0], [1.0, 0.0, 0.0])
        plot_objects((self.building, ray_plotter), colors=colors)

        print(hits)

        return


@njit
def simulation_loop(
    # Simulation setup
    num_steps: int,
    num_rays: int,
    source: PointType,
    sinks: PointType,
    # Building in the array format
    points: PointType,
    faces: IndexType,
    polygons: IndexType,
    walls: IndexType,
    solids: IndexType,
    zones: IndexType,
    trans_poly_nums: set[int],
) -> tuple[PointType, IntDataType]:
    """Simulation loop compiled to machine code with Numba.
    """
    hits = np.zeros(len(sinks))

    # Simulation parameters (TODO: add to config and/or property dict)
    t_step = 1e-4
    absorption = 0.1
    sink_radius = 0.1

    # Initial energy
    energy = np.ones(num_rays)

    # Direction and velocity
    speed = 343.
    direction = np.random.rand(num_rays, 3) * 2.0 - 1.0
    for i in range(num_rays):
        direction[i] /= np.linalg.norm(direction[i])
    velocity = direction * speed
    delta_pos = velocity * t_step

    # Initial position
    pos = np.zeros((num_rays, 3))
    for i in range(num_rays):
        pos[i, :] = source.copy()

    # Distance to each sink
    num_sinks = sinks.shape[0]
    sink_dist = np.zeros((num_sinks, num_rays))
    for sn in range(num_sinks):
        sink_dist[sn, :] = np.sqrt(np.sum((pos - sinks[sn])**2, axis=1))

    # Target surfaces
    target_surfs: IndexType = find_target_surfaces(
        pos,
        direction,
        points,
        faces,
        polygons,
        walls,
        solids,
        zones,
        trans_poly_nums,
    )

    # Move rays
    for i in range(num_steps):
        for rn in range(num_rays):
            if energy[rn] == 0.0:
                continue

            pos[rn] += delta_pos[rn]

            # Check sinks
            for sn in range(num_sinks):
                sink_dist[sn, rn] = np.sqrt(np.sum((pos[rn] - sinks[sn])**2))

                if sink_dist[sn, rn] < sink_radius:
                    hits[sn] += energy[rn]
                    energy[rn] = 0.0

            # Reflections
            ...

    return pos, hits


@njit
def find_target_surfaces(
    # Rays
    pos: PointType,
    direction: VectorType,
    # Building
    points: PointType,
    faces: IndexType,
    polygons: IndexType,
    walls: IndexType,
    solids: IndexType,
    zones: IndexType,
    trans_poly_nums: set[int],
) -> IndexType:
    pts, tri = get_polygon_pts_and_tri(0, points, faces, polygons)  # WIP
    breakpoint()
    pass


@njit
def get_polygon_pts_and_tri(
    poly_num,
    points,
    faces,
    polygons,
) -> tuple[PointType, IndexType]:
    """Returns polygon points and faces for a given polygon number.
    """
    # Get faces of the selected polygon
    poly_faces = faces[polygons == poly_num]

    # Point indices needs to be renumbered, a mapping from old to new numbers is needed
    face_remap = {}

    # Point numbers - this list is used to collect the needed points
    pt_nums = []

    new_index = 0
    for old_index in poly_faces.flatten():
        if old_index not in face_remap:  # We don't want to take a point index twice
            face_remap[old_index] = new_index
            pt_nums.append(old_index)
            new_index += 1

    # Collect the points
    num_points = len(pt_nums)
    poly_points = np.zeros((num_points, 3), dtype=FLOAT)

    for i in range(num_points):
        poly_points[i] = points[pt_nums[i]]

    # Re-number face point indices
    new_faces = np.zeros_like(poly_faces, dtype=INT)
    for fn, fc in enumerate(poly_faces):
        for pn in range(3):
            new_faces[fn, pn] = face_remap[fc[pn]]

    return poly_points, new_faces
