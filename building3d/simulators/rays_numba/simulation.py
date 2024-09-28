from numba import njit
import numpy as np

from building3d.io.arrayformat import to_array_format
from building3d.io.arrayformat import get_polygon_points_and_faces
from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.polygon import Polygon
from building3d.geom.polygon.distance import distance_point_to_polygon
from building3d.geom.types import PointType, VectorType, IndexType, IntDataType, FLOAT, INT
from building3d.geom.vectors import normal
from building3d.display.plot_objects import plot_objects
from .bvh import make_bvh_grid
from .find_target import find_target_surface
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
            transparent_polygons = trans_poly_nums,
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
    transparent_polygons: set[int],
) -> tuple[PointType, IntDataType]:
    """Simulation loop compiled to machine code with Numba.
    """
    # Simulation parameters (TODO: add to config and/or property dict)
    t_step = 1e-4
    absorption = 0.1
    sink_radius = 0.1

    # Initial ray energy and received energy
    energy = np.ones(num_rays, dtype=FLOAT)
    hits = np.zeros(len(sinks), dtype=FLOAT)

    # Direction and velocity
    speed = 343.
    init_direction = np.random.rand(num_rays, 3) * 2.0 - 1.0
    for i in range(num_rays):
        init_direction[i] /= np.linalg.norm(init_direction[i])
    velocity = init_direction * speed
    delta_pos = velocity * t_step
    reflection_dist = speed * t_step * 2.0

    # Get polygon points and faces
    poly_pts = []
    poly_tri = []
    num_polys = len(walls)
    for pn in range(num_polys):
        pts, tri = get_polygon_points_and_faces(points, faces, polygons, pn)
        poly_pts.append(pts)
        poly_tri.append(tri)

    # Make BVH grid
    grid_step = 0.2
    assert grid_step > speed * t_step, "Can't use grid smaller than ray position increment"

    min_x = points[:, 0].min()
    min_y = points[:, 1].min()
    min_z = points[:, 2].min()
    max_x = points[:, 0].max()
    max_y = points[:, 1].max()
    max_z = points[:, 2].max()

    grid = make_bvh_grid(
        min_xyz = (min_x, min_y, min_z),
        max_xyz = (max_x, max_y, max_z),
        poly_pts = poly_pts,
        poly_tri = poly_tri,
        step = grid_step,
    )

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
    # If the index of the target is -1, it means that the target surface is unknown.
    # Target surface may be unknown when it is far away, because we only look at nearby polygons.
    target_surfs = np.full(num_rays, -1, dtype=np.int32)

    # Move rays
    for i in range(num_steps):
        print("Step", i)
        for rn in range(num_rays):
            if energy[rn] <= 0.0:
                continue

            pos[rn] += delta_pos[rn]

            # Check sinks
            for sn in range(num_sinks):
                sink_dist[sn, rn] = np.sqrt(np.sum((pos[rn] - sinks[sn])**2))

                if sink_dist[sn, rn] < sink_radius:
                    hits[sn] += energy[rn]
                    energy[rn] = 0.0

            # Check near polygons
            x = int(pos[rn][0] / grid_step)
            y = int(pos[rn][1] / grid_step)
            z = int(pos[rn][2] / grid_step)

            # Get a set of nearby polygon indices to check if the ray
            # is not going to move outside the building in the next step.
            # Need to find the target surface and calculate distance from it.
            polygons_to_check = set()
            for i in range(-1, 2, 1):
                for j in range(-1, 2, 1):
                    for k in range(-1, 2, 1):
                        if (x + i, y + j, z + k) in grid:
                            poly_indices = grid[(x + i, y + j, z + k)]
                            for index in poly_indices:
                                polygons_to_check.add(index)

            target_surfs[rn] = find_target_surface(
                pos[rn],
                velocity[rn],
                poly_pts,
                poly_tri,
                transparent_polygons,
                polygons_to_check,
            )
            pts = poly_pts[target_surfs[rn]]
            tri = poly_tri[target_surfs[rn]]
            vn = normal(pts[-1], pts[0], pts[1])
            dist = distance_point_to_polygon(pos[rn], pts, tri, vn)

            while target_surfs[rn] >= 0 and dist < reflection_dist and energy[rn] > 0:
                # Reflect from the target polygon
                # print("Reflect ray", rn, "from", target_surfs[rn], "; energy=", energy[rn])
                dot = np.dot(vn, velocity[rn])
                velocity[rn] = velocity[rn] - 2 * dot * vn
                delta_pos[rn] = velocity[rn] * t_step
                energy[rn] -= absorption

                if energy[rn] < 0:
                    energy[rn] = 0.0
                    break

                # Get a set of nearby polygon indices to check if the ray
                # is not going to move outside the building in the next step.
                # Need to find the target surface and calculate distance from it.
                polygons_to_check = set()
                for i in range(-1, 2, 1):
                    for j in range(-1, 2, 1):
                        for k in range(-1, 2, 1):
                            if (x + i, y + j, z + k) in grid:
                                poly_indices = grid[(x + i, y + j, z + k)]
                                for index in poly_indices:
                                    polygons_to_check.add(index)

                target_surfs[rn] = find_target_surface(
                    pos[rn],
                    velocity[rn],
                    poly_pts,
                    poly_tri,
                    transparent_polygons,
                    polygons_to_check,
                )
                pts = poly_pts[target_surfs[rn]]
                tri = poly_tri[target_surfs[rn]]
                vn = normal(pts[-1], pts[0], pts[1])
                dist = distance_point_to_polygon(pos[rn], pts, tri, vn)

    return pos, hits
