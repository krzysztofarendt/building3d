"""Rotation functions."""

from numba import njit
import numpy as np
from numpy.typing import NDArray

from .vectors import angle
from .vectors import normal
from .points import new_point, points_equal
from .types import PointType, VectorType, FLOAT
from building3d.config import GEOM_ATOL


@njit
def rotation_matrix(u: VectorType, phi: float) -> NDArray[FLOAT]:
    """Calculate rotation matrix for a unit vector u and angle phi.

    A rotation in 3D can be described with an axis and angle around that axis.
    The axis is described with a unit vector u (ux**2 + uy**2 + uz**2 == 1)
    a vector phi (in radians).
    """
    # Rotation matrix
    # Reference: https://en.wikipedia.org/wiki/Rotation_matrix#Basic_3D_rotations
    # Method 1 (less stable numerically):
    # R = np.array([
    #     [
    #         np.cos(phi) + u[0]**2 * (1 - np.cos(phi)),
    #         u[0] * u[1] * (1 - np.cos(phi)) - u[2] * np.sin(phi),
    #         u[0] * u[2] * (1 - np.cos(phi)) + u[1] * np.sin(phi),
    #     ],
    #     [
    #         u[1] * u[0] * (1 - np.cos(phi)) + u[2] * np.sin(phi),
    #         np.cos(phi) + u[1] ** 2 * (1 - np.cos(phi)),
    #         u[1] * u[2] * (1 - np.cos(phi)) - u[0] * np.sin(phi),
    #     ],
    #     [
    #         u[2] * u[0] * (1 - np.cos(phi)) - u[1] * np.sin(phi),
    #         u[2] * u[1] * (1 - np.cos(phi)) + u[0] * np.sin(phi),
    #         np.cos(phi) + u[2] ** 2 * (1 - np.cos(phi)),
    #     ],
    # ])
    # Method 2 (more stable numerically):
    # https://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula
    # https://math.stackexchange.com/questions/142821/matrix-for-rotation-around-a-vector
    assert np.isclose(
        np.linalg.norm(u), 1.0
    ), "rotation_matrix() requires u to be a unit vector"

    W = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    R = np.eye(3) + np.sin(phi) * W + (2 * np.sin(phi / 2) ** 2) * np.dot(W, W)

    return R


@njit
def rotate_points(pts: PointType, R: NDArray[FLOAT]) -> PointType:
    """Rotate points using rotation matrix R."""
    return pts.dot(R.T)


@njit
def rotate_points_around_vector(
    pts: PointType, u: VectorType, phi: float
) -> tuple[PointType, NDArray[FLOAT]]:
    """Rotate points around the unit vector u with the angle phi (radians).

    Args:
        pts: list of points to be rotated
        u: normal vector of the rotation axis
        phi: rotation angle in radians

    Return:
        (list of rotated points, rotation matrix)
    """
    if np.linalg.norm(u) < GEOM_ATOL or abs(phi) < GEOM_ATOL:
        # No need to rotate
        return pts, np.ones((3, 3))

    # Rotate the points
    R = rotation_matrix(u, phi)

    # Convert points to list of Points
    rotated_pts = rotate_points(pts, R)

    return rotated_pts, R


@njit
def rotate_points_to_plane(
    pts: PointType, anchor: PointType, u: VectorType, d: float = 0.0
) -> tuple[PointType, NDArray[FLOAT], float]:
    """Rotate and translate points to a plane defined by a normal vec. and dist. from origin d.

    If anchor is not Point(0.0, 0.0, 0.0) and d is not 0.0, then points are also translated!

    Args:
        pts: list of points to be rotated
        anchor: rotation center point
        u: normal vector of the new plane (rotation)
        d: distance from origin (0,0,0) of the new plane (translation) (default 0.0)

    Return:
        (list of rotated points, rotation axis, rotation angle)
    """
    # Find normal to the points
    p_norm = normal(pts[-1], pts[0], pts[1])

    # Move points to anchor
    if not points_equal(anchor, new_point(0.0, 0.0, 0.0)):
        pts = pts - anchor

    # Find rotation axis
    rotaxis = np.cross(p_norm, u)
    if (np.abs(rotaxis) < GEOM_ATOL).all():
        # No need to rotate, the points are already at the correct plane
        phi = 0.0
        return pts, rotaxis, phi

    rotaxis /= np.linalg.norm(rotaxis)

    # Find rotation angle
    phi = angle(p_norm, u)

    # Rotate the points
    R = rotation_matrix(rotaxis, float(phi))
    pts = pts.dot(R.T)

    # Move points back from anchor
    if not points_equal(anchor, new_point(0.0, 0.0, 0.0)):
        pts += anchor

    # Move points to d (translation)
    p_dest = u * d
    pts += p_dest

    return pts, rotaxis, float(phi)
