import numpy as np
from numba import njit
from numba import prange

from building3d.geom.polygon.distance import distance_point_to_polygon
from building3d.geom.types import FLOAT
from building3d.geom.types import FloatDataType
from building3d.geom.types import IndexType
from building3d.geom.types import PointType
from building3d.geom.types import VectorType
from building3d.geom.vectors import normal
from building3d.io.arrayformat import get_polygon_points_and_faces
from building3d.types.cyclic_buffer import convert_to_contiguous
from building3d.types.cyclic_buffer import cyclic_buf

from .find_nearby_polygons import find_nearby_polygons
from .find_target import find_target_surface
from .voxel_grid import make_voxel_grid


@njit(parallel=True)
def simulation_loop(
    num_steps: int,
    num_rays: int,
    ray_speed: float,
    time_step: float,
    grid_step: float,
    source: PointType,
    absorbers: PointType,
    absorber_radius: float,
    points: PointType,
    faces: IndexType,
    polygons: IndexType,
    walls: IndexType,
    transparent_polygons: set[int],
    surf_absorption: FloatDataType,
    buffer_size: int,
    eps: float = 1e-6,
) -> tuple[PointType, VectorType, FloatDataType, FloatDataType]:
    """Performs a simulation loop for ray tracing in a building environment.

    This function is compiled to machine code with Numba for improved performance. It simulates
    the movement of rays through a building, handling reflections, absorptions, and hits on absorbers.

    Args:
        num_steps (int): Number of simulation steps to perform.
        num_rays (int): Number of rays to simulate.
        ray_speed (float): Speed of rays in m/s.
        time_step (float): Simulation time step in seconds.
        grid_step (float): Voxel grid step size.
        source (PointType): Starting point for all rays.
        absorbers (PointType): Array of absorber positions.
        absorber_radius (float): Size of absorbers.
        points (PointType): Array of all points in the building geometry.
        faces (IndexType): Array of face indices for the building geometry.
        polygons (IndexType): Array of polygon indices for the building geometry.
        walls (IndexType): Array of wall indices for the building geometry.
        transparent_polygons (set[int]): Set of indices for transparent polygons.
        surf_absorbtion (FloatDataType): Absorption coefficients for each polygon,
                                         shape (len(polygons), ).
        buffer_size (int): Size of buffers used to store part positions, energy, hits.
        eps (float): Small number used in comparison operations.

    Returns:
        tuple[PointType, PointType, PointType, IntDataType]: A tuple containing:
            - pos_buf: buffer of ray positions, shaped (num_steps + 1, num_rays, 3)
            - vel_buf: buffer of ray velocity, shaped (num_steps + 1, num_rays, 3)
            - enr_buf: buffer of ray energy, shaped (num_steps + 1, num_rays)
            - hit_buf: buffer of ray absorber hits, shaped (num_steps + 1, num_rays)
    """
    print("Simulation loop started")
    if len(transparent_polygons) > 1:
        transparent_polygons.remove(-1)

    # Initial ray energy and received energy
    energy = np.ones(num_rays, dtype=FLOAT)
    hits = np.zeros(len(absorbers), dtype=FLOAT)

    # Direction and velocity
    init_direction = np.random.rand(num_rays, 3) * 2.0 - 1.0
    for i in range(num_rays):
        init_direction[i] /= np.linalg.norm(init_direction[i])
    velocity = init_direction * ray_speed
    delta_pos = velocity * time_step
    just_in_case_margin = 1.01
    reflection_dist = ray_speed * time_step * just_in_case_margin

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
    grid_step = grid_step
    assert (
        grid_step > reflection_dist
    ), "Can't use grid smaller than reflection distance"

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
        min_xyz=(min_x, min_y, min_z),
        max_xyz=(max_x, max_y, max_z),
        poly_pts=poly_pts,
        step=grid_step,
    )

    # Initial position
    print("Initializing arrays: position, velocity, energy, hits")
    pos = np.zeros((num_rays, 3), dtype=FLOAT)
    for i in range(num_rays):
        pos[i, :] = source.copy()

    # Cyclic buffers
    pos_buf = np.zeros((buffer_size, num_rays, 3), dtype=FLOAT)
    for _ in range(3):
        pos_buf[:, :, :] = source.copy()
    vel_buf = np.zeros((buffer_size, num_rays, 3), dtype=FLOAT)
    enr_buf = np.ones((buffer_size, num_rays), dtype=FLOAT)
    hit_buf = np.zeros((buffer_size, len(absorbers)), dtype=FLOAT)

    pos_head, pos_tail = 0, 0
    vel_head, vel_tail = 0, 0
    enr_head, enr_tail = 0, 0
    hit_head, hit_tail = 0, 0

    # Update cyclic buffers
    pos_buf, pos_head, pos_tail = cyclic_buf(
        pos_buf, pos_head, pos_tail, pos, buffer_size
    )
    vel_buf, vel_head, vel_tail = cyclic_buf(
        vel_buf, vel_head, vel_tail, velocity, buffer_size
    )
    enr_buf, enr_head, enr_tail = cyclic_buf(
        enr_buf, enr_head, enr_tail, energy, buffer_size
    )
    hit_buf, hit_head, hit_tail = cyclic_buf(
        hit_buf, hit_head, hit_tail, hits, buffer_size
    )

    # Distance to each absorber
    print("Calculating initial distance to each absorber")
    num_absorbers = absorbers.shape[0]
    absorber_dist = np.zeros((num_absorbers, num_rays))
    for sn in range(num_absorbers):
        absorber_dist[sn, :] = np.sqrt(np.sum((pos - absorbers[sn]) ** 2, axis=1))

    # Target surfaces
    # If the index of the target is -1, it means that the target surface is unknown.
    # Target surface may be unknown when it is far away, because we only look at nearby polygons.
    target_surfs = np.full(num_rays, -1, dtype=np.int32)

    # Move rays
    print("Entering the loop")
    for i in range(num_steps):
        print("Step", i, "| total energy =", energy.sum())
        # Check absorbers
        # This probably shouldn't be inside prange, because of the hits array
        for rn in range(num_rays):
            for sn in range(num_absorbers):
                # TODO: Switch to squared distances to avoid calculating sqrt in each iteration
                absorber_dist[sn, rn] = np.sqrt(np.sum((pos[rn] - absorbers[sn]) ** 2))
                if absorber_dist[sn, rn] < absorber_radius:
                    hits[sn] += energy[rn]  # This line shouldn't be inside prange
                    energy[rn] = 0.0

        for rn in prange(num_rays):
            # If the ray somehow left the building - set its energy to 0
            if energy[rn] > 0 and (
                pos[rn][0] < min_x - eps
                or pos[rn][1] < min_y - eps
                or pos[rn][2] < min_z - eps
                or pos[rn][0] > max_x + eps
                or pos[rn][1] > max_y + eps
                or pos[rn][2] > max_z + eps
            ):
                energy[rn] = 0.0

            # If energy is null, the ray should not move
            if energy[rn] <= eps:
                continue

            # Check near polygons
            x = int(np.floor(pos[rn][0] / grid_step))
            y = int(np.floor(pos[rn][1] / grid_step))
            z = int(np.floor(pos[rn][2] / grid_step))

            # Get a set of nearby polygon indices to check the ray distance to next wall
            polygons_to_check = find_nearby_polygons(x, y, z, grid)

            target_surfs[rn] = find_target_surface(
                pos[rn],
                velocity[rn],
                poly_pts,
                poly_tri,
                transparent_polygons,
                polygons_to_check,
                atol=1e-3,
            )
            # If the next surface is known, calculate the distance to it.
            # If not, assume infinity.
            if target_surfs[rn] >= 0:
                pts = poly_pts[target_surfs[rn]]
                tri = poly_tri[target_surfs[rn]]
                vn = normal(pts[-1], pts[0], pts[1])
                dist = distance_point_to_polygon(pos[rn], pts, tri, vn)
            else:
                vn = np.zeros(3, dtype=FLOAT)
                dist = np.inf

            while target_surfs[rn] >= 0 and dist < reflection_dist and energy[rn] > eps:
                # Reflect from the target polygon
                energy[rn] -= surf_absorption[target_surfs[rn]]
                if energy[rn] <= eps:
                    energy[rn] = 0.0
                    break

                # Assert statement does not work with prange...
                # assert np.linalg.norm(vn) > 0, "Normal vector cannot have zero length"
                dot = np.dot(vn, velocity[rn])
                velocity[rn] = velocity[rn] - 2 * dot * vn
                delta_pos[rn] = velocity[rn] * time_step

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
                    atol=1e-3,
                )
                # If the next surface is known, calculate the distance to it.
                # If not, assume infinity.
                # TODO: These lines are repeated and could be turned into a function.
                if target_surfs[rn] >= 0:
                    pts = poly_pts[target_surfs[rn]]
                    tri = poly_tri[target_surfs[rn]]
                    vn = normal(pts[-1], pts[0], pts[1])
                    dist = distance_point_to_polygon(pos[rn], pts, tri, vn)
                else:
                    vn = np.zeros(3, dtype=FLOAT)
                    dist = np.inf

            if energy[rn] > eps and dist > reflection_dist:
                pos[rn] += delta_pos[rn]
            else:
                continue

        # Update cyclic buffers
        pos_buf, pos_head, pos_tail = cyclic_buf(
            pos_buf, pos_head, pos_tail, pos, buffer_size
        )
        vel_buf, vel_head, vel_tail = cyclic_buf(
            vel_buf, vel_head, vel_tail, velocity, buffer_size
        )
        enr_buf, enr_head, enr_tail = cyclic_buf(
            enr_buf, enr_head, enr_tail, energy, buffer_size
        )
        hit_buf, hit_head, hit_tail = cyclic_buf(
            hit_buf, hit_head, hit_tail, hits, buffer_size
        )

    print("Exiting the loop")
    print("Converting buffers to contiguous arrays")
    pos_buf = convert_to_contiguous(pos_buf, pos_head, pos_tail, buffer_size)
    vel_buf = convert_to_contiguous(vel_buf, vel_head, vel_tail, buffer_size)
    enr_buf = convert_to_contiguous(enr_buf, enr_head, enr_tail, buffer_size)
    hit_buf = convert_to_contiguous(hit_buf, hit_head, hit_tail, buffer_size)

    print("Exiting the function")
    # Shapes:
    # pos_buf: (num_steps + 1, num_rays, 3)
    # vel_buf: (num_steps + 1, num_rays, 3)
    # enr_buf: (num_steps + 1, num_rays)
    # enr_buf: (num_steps + 1, num_rays)
    # First shape is 1 larger than num_steps to include the initial state.
    return pos_buf, vel_buf, enr_buf, hit_buf
