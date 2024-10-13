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
from .voxel_grid import make_voxel_grid
from .find_target import find_target_surface
from .find_transparent import find_transparent
from .find_nearby_polygons import find_nearby_polygons
from .cyclic_buffer import cyclic_buf, convert_to_contiguous
from .config import BUFF_SIZE, GRID_STEP, T_STEP, SPEED, ABSORB, SINK_RADIUS


logger = logging.getLogger(__name__)


class Simulation:

    def __init__(
        self,
        building: Building,
        source: PointType,
        absorbers: PointType,
        num_rays: int,
        num_steps: int,
        search_transparent: bool = True,
    ):
        self.building = building
        self.source = source.copy()
        self.absorbers = absorbers.copy()
        self.num_rays = num_rays
        self.num_steps = num_steps
        self.search_transparent = search_transparent

    def run(self):
        # Get transparent polygons
        logger.info("Finding transparent surfaces")
        if self.search_transparent:
            # TODO: Very slow if many polygons
            # Complexity:
            # - worst case scenario -> O(n^2),
            # - best case scenario -> O(n),
            # where n is the number of polygons.
            trans_poly_paths = find_transparent(self.building)
        else:
            trans_poly_paths = set()

        # Can't have an empty set because of Numba. Polygon -1 doesn't exist anyway.
        trans_poly_nums = set([-1])
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
    eps: float = 1e-6,
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
    print("Simulation loop started")
    # Simulation parameters
    t_step = T_STEP
    absorption = ABSORB
    sink_radius = SINK_RADIUS

    # Initial ray energy and received energy
    energy = np.ones(num_rays, dtype=FLOAT)
    hits = np.zeros(len(absorbers), dtype=FLOAT)

    # Direction and velocity
    speed = SPEED
    init_direction = np.random.rand(num_rays, 3) * 2.0 - 1.0
    for i in range(num_rays):
        init_direction[i] /= np.linalg.norm(init_direction[i])
    velocity = init_direction * speed
    delta_pos = velocity * t_step
    just_in_case_margin = 1.01
    reflection_dist = speed * t_step * just_in_case_margin

    # Get polygon points and faces
    print("Collecting polygon points and faces from the array format")
    poly_pts = []
    poly_tri = []
    num_polys = len(walls)
    for pn in range(num_polys):
        pts, tri = get_polygon_points_and_faces(points, faces, polygons, pn)
        poly_pts.append(pts)
        poly_tri.append(tri)

    # Make voxel grid
    print("Making the voxel grid")
    grid_step = GRID_STEP
    assert grid_step > reflection_dist, "Can't use grid smaller than reflection distance"

    min_x = points[:, 0].min()
    min_y = points[:, 1].min()
    min_z = points[:, 2].min()
    max_x = points[:, 0].max()
    max_y = points[:, 1].max()
    max_z = points[:, 2].max()

    print("X limits:", min_x, max_x)
    print("Y limits:", min_y, max_y)
    print("Z limits:", min_z, max_z)

    grid = make_voxel_grid(
        min_xyz = (min_x, min_y, min_z),
        max_xyz = (max_x, max_y, max_z),
        poly_pts = poly_pts,
        poly_tri = poly_tri,
        step = grid_step,
    )

    # Initial position
    print("Initializing arrays: position, velocity, energy, hits")
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
    enr_buf, enr_head, enr_tail = cyclic_buf(enr_buf, enr_head, enr_tail, energy, BUFF_SIZE)
    hit_buf, hit_head, hit_tail = cyclic_buf(hit_buf, hit_head, hit_tail, hits, BUFF_SIZE)

    # Distance to each absorber
    print("Calculating initial distance to each absorber")
    num_absorbers = absorbers.shape[0]
    absorber_dist = np.zeros((num_absorbers, num_rays))
    for sn in range(num_absorbers):
        absorber_dist[sn, :] = np.sqrt(np.sum((pos - absorbers[sn])**2, axis=1))

    # Target surfaces
    # If the index of the target is -1, it means that the target surface is unknown.
    # Target surface may be unknown when it is far away, because we only look at nearby polygons.
    target_surfs = np.full(num_rays, -1, dtype=np.int32)

    # Move rays
    print("Entering the loop")
    for i in range(num_steps):
        print("Step", i)
        for rn in prange(num_rays):
            # If the ray somehow left the building - set its energy to 0
            if energy[rn] > 0 and (
                pos[rn][0] < min_x - eps or
                pos[rn][1] < min_y - eps or
                pos[rn][2] < min_z - eps or
                pos[rn][0] > max_x + eps or
                pos[rn][1] > max_y + eps or
                pos[rn][2] > max_z + eps
            ):
                energy[rn] = 0.0

            # If energy is null, the ray should not move
            if energy[rn] <= 0.0:
                continue

            pos[rn] += delta_pos[rn]

            # Check absorbers
            for sn in range(num_absorbers):
                # TODO: Switch to squared distances to avoid calculating sqrt in each iteration
                absorber_dist[sn, rn] = np.sqrt(np.sum((pos[rn] - absorbers[sn])**2))

                if absorber_dist[sn, rn] < sink_radius:
                    hits[sn] += energy[rn]
                    energy[rn] = 0.0

            # Check near polygons
            x = int(np.floor(pos[rn][0] / grid_step))
            y = int(np.floor(pos[rn][1] / grid_step))
            z = int(np.floor(pos[rn][2] / grid_step))

            # Get a set of nearby polygon indices to check the ray distance to next wall
            polygons_to_check = find_nearby_polygons(x, y, z, grid)  # TODO: Some rays are leaving
            # polygons_to_check = set(polygons)  # TODO: This works better with reflections

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

    print("Exiting the loop")
    print("Converting buffers to contiguous arrays")
    pos_buf = convert_to_contiguous(pos_buf, pos_head, pos_tail, BUFF_SIZE)
    vel_buf = convert_to_contiguous(vel_buf, vel_head, vel_tail, BUFF_SIZE)
    enr_buf = convert_to_contiguous(enr_buf, enr_head, enr_tail, BUFF_SIZE)
    hit_buf = convert_to_contiguous(hit_buf, hit_head, hit_tail, BUFF_SIZE)

    print("Exiting the function")
    return pos_buf, vel_buf, enr_buf, hit_buf
