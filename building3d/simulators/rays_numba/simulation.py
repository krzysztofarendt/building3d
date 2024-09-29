import logging

from numba import njit, prange
import numpy as np

from building3d.io.arrayformat import to_array_format
from building3d.io.arrayformat import get_polygon_points_and_faces
from building3d.geom.building import Building
from building3d.geom.polygon import Polygon
from building3d.geom.polygon.distance import distance_point_to_polygon
from building3d.geom.types import PointType, IndexType, IntDataType, FLOAT
from building3d.geom.vectors import normal
from .bvh import make_bvh_grid
from .find_target import find_target_surface
from .find_transparent import find_transparent
from .find_nearby_polygons import find_nearby_polygons
from .cyclic_buffer import cyclic_buf, convert_to_contiguous
from .config import BUFF_SIZE


logger = logging.getLogger(__name__)


class Simulation:

    def __init__(
        self,
        building: Building,
        source: PointType,
        absorbers: PointType,
        num_rays: int,
        num_steps: int,
    ):
        self.building = building
        self.source = source.copy()
        self.absorbers = absorbers.copy()
        self.num_rays = num_rays
        self.num_steps = num_steps

    def run(self):
        # Get transparent polygons
        logger.info("Finding transparent surfaces")
        # TODO: If below set is empty, Numba cannot guess the type
        # TODO: Very slow if many polygons
        trans_poly_paths = find_transparent(self.building)
        trans_poly_nums = set()
        for poly_path in trans_poly_paths:
            poly = self.building.get(poly_path)
            assert isinstance(poly, Polygon)
            trans_poly_nums.add(poly.num)

        # Convert building to the array format
        logger.info("Converting the building to the array format")
        points, faces, polygons, walls, solids, zones = to_array_format(self.building)

        # Run simulation loop (JIT compiled)
        logger.info("Starting the simulation")
        pos_buf, vel_buf, enr_buf, hit_buf = simulation_loop(
            self.num_steps,
            self.num_rays,
            source = self.source,
            absorbers = self.absorbers,
            points = points,
            faces = faces,
            polygons = polygons,
            walls = walls,
            transparent_polygons = trans_poly_nums,
        )
        logger.info("Finished the simulation")
        return pos_buf, vel_buf, enr_buf, hit_buf


@njit(parallel=True)
def simulation_loop(
    # Simulation setup
    num_steps: int,
    num_rays: int,
    source: PointType,
    absorbers: PointType,
    # Building in the array format
    points: PointType,
    faces: IndexType,
    polygons: IndexType,
    walls: IndexType,
    transparent_polygons: set[int],
) -> tuple[PointType, PointType, PointType, IntDataType]:
    """Performs a simulation loop for ray tracing in a building environment.

    This function is compiled to machine code with Numba for improved performance. It simulates
    the movement of rays through a building, handling reflections, absorptions, and hits on absorbers.

    Args:
        num_steps (int): Number of simulation steps to perform.
        num_rays (int): Number of rays to simulate.
        source (PointType): Starting point for all rays.
        absorbers (PointType): Array of absorber positions.
        points (PointType): Array of all points in the building geometry.
        faces (IndexType): Array of face indices for the building geometry.
        polygons (IndexType): Array of polygon indices for the building geometry.
        walls (IndexType): Array of wall indices for the building geometry.
        transparent_polygons (set[int]): Set of indices for transparent polygons.

    Returns:
        tuple[PointType, PointType, PointType, IntDataType]: A tuple containing:
            - pos_buf: Buffer of ray positions over time.
            - vel_buf: Buffer of ray velocities over time.
            - enr_buf: Buffer of ray energies over time.
            - hit_buf: Buffer of hit counts for each sink over time.
    """
    # Simulation parameters (TODO: add to config and/or property dict)
    t_step = 1e-5
    absorption = 0.1
    sink_radius = 0.1

    # Initial ray energy and received energy
    energy = np.ones(num_rays, dtype=FLOAT)
    hits = np.zeros(len(absorbers), dtype=FLOAT)

    # Direction and velocity
    speed = 343.
    init_direction = np.random.rand(num_rays, 3) * 2.0 - 1.0
    for i in range(num_rays):
        init_direction[i] /= np.linalg.norm(init_direction[i])
    velocity = init_direction * speed
    delta_pos = velocity * t_step
    reflection_dist = speed * t_step * 1.001

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
    pos = np.zeros((num_rays, 3), dtype=FLOAT)
    for i in range(num_rays):
        pos[i, :] = source.copy()

    # Cyclic buffers
    pos_buf = np.zeros((BUFF_SIZE, num_rays, 3), dtype=FLOAT)
    for _ in range(3):
        pos_buf[:, :, :] = source.copy()
    vel_buf = np.zeros((BUFF_SIZE, num_rays, 3), dtype=FLOAT)
    enr_buf = np.ones((BUFF_SIZE, num_rays), dtype=FLOAT)
    hit_buf = np.zeros((BUFF_SIZE, len(absorbers)), dtype=FLOAT)

    pos_head, pos_tail = 0, 0
    vel_head, vel_tail = 0, 0
    enr_head, enr_tail = 0, 0
    hit_head, hit_tail = 0, 0

    # Update cyclic buffers
    pos_buf, pos_head, pos_tail = cyclic_buf(pos_buf, pos_head, pos_tail, pos, BUFF_SIZE)
    vel_buf, vel_head, vel_tail = cyclic_buf(vel_buf, vel_head, vel_tail, velocity, BUFF_SIZE)
    enr_buf, enr_head, vel_tail = cyclic_buf(enr_buf, enr_head, enr_tail, energy, BUFF_SIZE)
    hit_buf, hit_head, hit_tail = cyclic_buf(hit_buf, hit_head, hit_tail, hits, BUFF_SIZE)

    # Distance to each sink
    num_absorbers = absorbers.shape[0]
    sink_dist = np.zeros((num_absorbers, num_rays))
    for sn in range(num_absorbers):
        sink_dist[sn, :] = np.sqrt(np.sum((pos - absorbers[sn])**2, axis=1))

    # Target surfaces
    # If the index of the target is -1, it means that the target surface is unknown.
    # Target surface may be unknown when it is far away, because we only look at nearby polygons.
    target_surfs = np.full(num_rays, -1, dtype=np.int32)

    # Move rays
    for i in range(num_steps):
        print("Step", i)
        for rn in prange(num_rays):
            if energy[rn] <= 0.0:
                continue

            pos[rn] += delta_pos[rn]

            # Check absorbers
            for sn in range(num_absorbers):
                sink_dist[sn, rn] = np.sqrt(np.sum((pos[rn] - absorbers[sn])**2))

                if sink_dist[sn, rn] < sink_radius:
                    hits[sn] += energy[rn]
                    energy[rn] = 0.0

            # Check near polygons
            x = int(pos[rn][0] / grid_step)
            y = int(pos[rn][1] / grid_step)
            z = int(pos[rn][2] / grid_step)

            # Get a set of nearby polygon indices to check the ray distance to next wall
            polygons_to_check = find_nearby_polygons(x, y, z, grid)

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
                dot = np.dot(vn, velocity[rn])
                velocity[rn] = velocity[rn] - 2 * dot * vn
                delta_pos[rn] = velocity[rn] * t_step
                energy[rn] -= absorption

                if energy[rn] < 0:
                    energy[rn] = 0.0
                    break

                # Get a set of nearby polygon indices to check if the ray
                # is not going to move outside the building in the next step (after reflection).
                # Need to find the target surface and calculate distance from it.
                polygons_to_check = find_nearby_polygons(x, y, z, grid)

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

        # Update cyclic buffers
        pos_buf, pos_head, pos_tail = cyclic_buf(pos_buf, pos_head, pos_tail, pos, BUFF_SIZE)
        vel_buf, vel_head, vel_tail = cyclic_buf(vel_buf, vel_head, vel_tail, velocity, BUFF_SIZE)
        enr_buf, enr_head, enr_tail = cyclic_buf(enr_buf, enr_head, enr_tail, energy, BUFF_SIZE)
        hit_buf, hit_head, hit_tail = cyclic_buf(hit_buf, hit_head, hit_tail, hits, BUFF_SIZE)

    pos_buf = convert_to_contiguous(pos_buf, pos_head, pos_tail, BUFF_SIZE)
    vel_buf = convert_to_contiguous(vel_buf, vel_head, vel_tail, BUFF_SIZE)
    enr_buf = convert_to_contiguous(enr_buf, enr_head, enr_tail, BUFF_SIZE)
    hit_buf = convert_to_contiguous(hit_buf, hit_head, hit_tail, BUFF_SIZE)

    return pos_buf, vel_buf, enr_buf, hit_buf
