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

from .find_nearby_polygons import find_nearby_polygons
from .find_target import find_target_surface
from .voxel_grid import make_voxel_grid
from .jit_print import jit_print


@njit(parallel=True)
def simulation_loop(
    num_steps: int,
    num_rays: int,
    ray_speed: float,
    time_step: float,
    grid_step: float,
    position: PointType,
    velocity: VectorType,
    energy: FloatDataType,
    hits: FloatDataType,
    absorbers: PointType,
    absorber_radius: float,
    points: PointType,
    faces: IndexType,
    polygons: IndexType,
    walls: IndexType,
    transparent_polygons: set[int],
    surf_absorption: FloatDataType,
    verbose: bool = True,
    eps: float = 1e-6,
) -> tuple[PointType, FloatDataType, FloatDataType]:
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
        position (PointType): Current position of all rays.
        velocity (VectorType): Current velocity of all rays.
        absorbers (PointType): Array of absorber positions.
        absorber_radius (float): Size of absorbers.
        points (PointType): Array of all points in the building geometry.
        faces (IndexType): Array of face indices for the building geometry.
        polygons (IndexType): Array of polygon indices for the building geometry.
        walls (IndexType): Array of wall indices for the building geometry.
        transparent_polygons (set[int]): Set of indices for transparent polygons.
        surf_absorption (FloatDataType): Absorption coefficients for each polygon,
                                         shape (len(polygons), ).
        verbose (bool): Prints progress if True
        eps (float): Small number used in comparison operations.

    Returns:
        tuple[PointType, FloatDataType, FloatDataType]: A tuple containing:
            - pos_buf: buffer of ray positions, shaped (num_steps + 1, num_rays, 3)
            - enr_buf: buffer of ray energy, shaped (num_steps + 1, num_rays)
            - hit_buf: buffer of ray absorber hits, shaped (num_steps + 1, num_rays)
    """
    jit_print(verbose, "Simulation loop started")
    if len(transparent_polygons) > 1:
        transparent_polygons.remove(-1)

    # Absorber size as a squared radius (to avoid calculating sqrt for each ray and step)
    absorber_sq_radius = absorber_radius ** 2

    # Assume refleciton distance
    delta_pos = velocity * time_step
    just_in_case_margin = 1.01
    reflection_dist = ray_speed * time_step * just_in_case_margin

    # Get polygon points and faces
    jit_print(verbose, "Collecting polygon points and faces from the array format")
    poly_pts = []
    poly_tri = []
    num_polys = len(walls)
    for pn in range(num_polys):
        pts, tri = get_polygon_points_and_faces(points, faces, polygons, pn)
        poly_pts.append(pts)
        poly_tri.append(tri)

    # Make voxel grid
    jit_print(verbose, "Making the voxel grid")
    assert (
        grid_step > reflection_dist
    ), "Can't use grid smaller than reflection distance"

    min_x = points[:, 0].min()
    min_y = points[:, 1].min()
    min_z = points[:, 2].min()
    max_x = points[:, 0].max()
    max_y = points[:, 1].max()
    max_z = points[:, 2].max()

    jit_print(verbose, "X limits:", min_x, max_x)
    jit_print(verbose, "Y limits:", min_y, max_y)
    jit_print(verbose, "Z limits:", min_z, max_z)

    grid = make_voxel_grid(
        min_xyz=(min_x, min_y, min_z),
        max_xyz=(max_x, max_y, max_z),
        poly_pts=poly_pts,
        step=grid_step,
        verbose=verbose,
    )

    # Cyclic buffers
    buffer_size = num_steps + 1
    pos_buf = np.zeros((buffer_size, num_rays, 3), dtype=FLOAT)
    enr_buf = np.ones((buffer_size, num_rays), dtype=FLOAT)
    hit_buf = np.zeros((buffer_size, len(absorbers)), dtype=FLOAT)

    # Fill buffers with initial values
    pos_buf[0, :, :] = position
    enr_buf[0, :] = energy
    hit_buf[0, :] = hits

    # Distance to each absorber
    jit_print(verbose, "Calculating initial distance to each absorber")
    num_absorbers = absorbers.shape[0]
    absorber_sq_dist = np.zeros((num_absorbers, num_rays))
    for sn in range(num_absorbers):
        absorber_sq_dist[sn, :] = np.sum((position - absorbers[sn]) ** 2, axis=1)

    # Target surfaces
    # If the index of the target is -1, it means that the target surface is unknown.
    # Target surface may be unknown when it is far away, because we only look at nearby polygons.
    target_surfs = np.full(num_rays, -1, dtype=np.int32)

    # Move rays
    jit_print(verbose, "Entering the loop")
    for i in range(num_steps):
        jit_print(verbose, "Step", i, "| total energy =", energy.sum())

        # Reset hits for each absorber
        hits[:] = 0.0

        # Check absorbers
        # This probably shouldn't be inside prange, because of the hits array
        for rn in range(num_rays):
            if energy[rn] <= eps:
                continue
            for sn in range(num_absorbers):
                absorber_sq_dist[sn, rn] = np.sum((position[rn] - absorbers[sn]) ** 2)
                if absorber_sq_dist[sn, rn] < absorber_sq_radius:
                    hits[sn] += energy[rn]  # This line shouldn't be inside prange
                    energy[rn] = 0.0

        for rn in prange(num_rays):
            # If energy is null, the ray should not move
            if energy[rn] <= eps:
                continue

            # If the ray somehow left the building - set its energy to 0
            if energy[rn] > 0 and (
                position[rn][0] < min_x - eps
                or position[rn][1] < min_y - eps
                or position[rn][2] < min_z - eps
                or position[rn][0] > max_x + eps
                or position[rn][1] > max_y + eps
                or position[rn][2] > max_z + eps
            ):
                energy[rn] = 0.0

            # Check near polygons
            x = int(np.floor(position[rn][0] / grid_step))
            y = int(np.floor(position[rn][1] / grid_step))
            z = int(np.floor(position[rn][2] / grid_step))

            # Get a set of nearby polygon indices to check the ray distance to next wall
            polygons_to_check = find_nearby_polygons(x, y, z, grid)

            target_surfs[rn] = find_target_surface(
                position[rn],
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
                dist = distance_point_to_polygon(position[rn], pts, tri, vn)
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
                    position[rn],
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
                    dist = distance_point_to_polygon(position[rn], pts, tri, vn)
                else:
                    vn = np.zeros(3, dtype=FLOAT)
                    dist = np.inf

            if energy[rn] > eps and dist > reflection_dist:
                position[rn] += delta_pos[rn]
            else:
                continue

        # Update cyclic buffers
        pos_buf[i+1, :, :] = position
        enr_buf[i+1, :] = energy
        hit_buf[i+1, :] = hits

    jit_print(verbose, "Exiting the simulation loop")

    # Shapes:
    # pos_buf: (num_steps + 1, num_rays, 3)
    # enr_buf: (num_steps + 1, num_rays)
    # enr_buf: (num_steps + 1, num_rays)
    # First shape is 1 larger than num_steps to include the initial state.
    return pos_buf, enr_buf, hit_buf
