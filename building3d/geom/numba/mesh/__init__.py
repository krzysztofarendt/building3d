from numba import njit
import numpy as np

from building3d.geom.numba.types import PointType, IndexType, FLOAT, INT


@njit
def vstack_mesh(
    t_pts: tuple[PointType, ...],
    t_tri: tuple[IndexType, ...],
) -> tuple[PointType, IndexType]:
    """Takes tuples of points and triangles and stacks them vertically.
    """
    num_objects = len(t_pts)
    assert num_objects == len(t_tri)

    num_pts_tot = 0
    num_tri_tot = 0
    num_pts_per_obj = {}
    num_tri_per_obj = {}

    # Allocate empty arrays for verts and faces
    for i in range(num_objects):
        num_pts_tot += t_pts[i].shape[0]
        num_tri_tot += t_tri[i].shape[0]
        num_pts_per_obj[i] = t_pts[i].shape[0]
        num_tri_per_obj[i] = t_tri[i].shape[0]

    verts = np.zeros((num_pts_tot, 3), dtype=FLOAT)
    faces = np.zeros((num_tri_tot, 3), dtype=INT)

    # Fill the arrays (vstack)
    num_pts_added = 0
    tri_offset = 0
    pts_offset = 0
    for i in range(num_objects):
        for j in range(t_tri[i].shape[0]):
            if j == 0 and i > 0:
                tri_offset += num_tri_per_obj[i-1]
            faces[j + tri_offset] = t_tri[i][j] + num_pts_added
        for j in range(t_pts[i].shape[0]):
            if j == 0 and i > 0:
                pts_offset += num_pts_per_obj[i-1]
            verts[j + pts_offset] = t_pts[i][j]
            num_pts_added += 1

    # TODO: Equal points should be merged. Look at building3d/mesh/quality/purge_mesh.py
    ...

    return verts, faces
