import numpy as np
from numba import njit

from building3d.config import GEOM_ATOL
from building3d.config import POINT_NUM_DEC
from .config import POINT_TYPE, INDEX_TYPE
from .vectors import normal


def point_to_str(pt: np.ndarray) -> str:
    # njit doesn't support f-strings
    assert pt.shape == (3, )
    return f"pt(x={pt[0]:.2f},y={pt[1]:.2f},z={pt[2]:.2f},id={hex(id(pt))})"


@njit
def points_equal(pt1: POINT_TYPE, pt2: POINT_TYPE, atol: float = GEOM_ATOL) -> bool:
    return np.allclose(pt1, pt2, atol=atol)


def point_to_hash(pt: POINT_TYPE, decimals: int = POINT_NUM_DEC) -> int:
    # njit doesn't support hash() and tuple()
    pt = np.round(pt, decimals=decimals)
    return hash(tuple(pt))


@njit
def are_points_coplanar(
    pts: POINT_TYPE,
    atol: float = GEOM_ATOL,
) -> bool:

    num_pts = pts.shape[0]
    if num_pts <= 3:
        return True

    if are_points_collinear(pts):
        return True  # collinear points are also coplanar

    # Calculate normal vector based on the first 3 points
    vec_n = np.full(3, np.nan)
    i = 0
    while np.isnan(vec_n).any():
        if i+2 >= num_pts:
            if are_points_coplanar(pts):
                return True
            else:
                raise RuntimeError("Points not coplanar, yet all normal vectors have zero length")

        vec_n = normal(pts[i], pts[i+1], pts[i+2])
        i += 1

    # Plane equation:
    # ax + by + cz + d = 0
    # (a, b, c) are taken from the normal vector
    # d is calculated by substituting one of the points
    ref = 0  # reference point index
    ref_pt = pts[ref]
    d = -1 * np.dot(vec_n, ref_pt)

    # Check if all points lay on the same plane
    for i in range(num_pts):
        coplanar = np.abs(d + np.dot(vec_n, pts[i])) < atol
        if not coplanar:
            return False
    return True


@njit
def are_points_collinear(
    pts: POINT_TYPE,
    atol: float = GEOM_ATOL,
) -> bool:
    num_pts = pts.shape[0]
    assert num_pts >= 3, "At least 3 points must be given"

    # Calculate unit vectors using the first point as origin
    vectors = np.zeros((num_pts - 1, 3))
    for i in range(1, num_pts):
        v_num = i - 1
        vectors[v_num] = pts[i] - pts[0]
        vectors[v_num] /= np.linalg.norm(vectors[v_num])

    are_collinear = True
    num_vectors = vectors.shape[0]
    for i in range(1, num_vectors):
        if (
            np.allclose(vectors[i], vectors[i-1], atol=atol)
            or
            np.allclose(vectors[i], -1 * vectors[i-1], atol=atol)
        ):
            pass
        else:
            are_collinear = False
            break

    return are_collinear
