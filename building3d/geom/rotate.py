"""Rotation functions."""
import numpy as np

from .point import Point
from .vector import angle
from .vector import normal
from .vector import length
from building3d.config import GEOM_EPSILON


def rotation_matrix(u: np.ndarray, phi: float) -> np.ndarray:
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
    assert np.isclose(length(u), 1.0), "rotation_matrix() requires u to be a unit vector"

    W = np.array([[0, -u[2], u[1]],
                  [u[2], 0, -u[0]],
                  [-u[1], u[0], 0]])
    R = np.eye(3) + np.sin(phi) * W + (2 * np.sin(phi/2) ** 2) * np.dot(W, W)

    return R


def rotate_points(points: list[Point], R: np.ndarray) -> list[Point]:
    pts_arr = np.array([p.vector() for p in points])
    pts_arr = pts_arr.dot(R.T)
    pts = [Point(x, y, z) for (x, y, z) in pts_arr]
    return pts


def rotate_points_around_vector(
    points: list[Point], u: np.ndarray, phi: float
) -> tuple[list[Point], np.ndarray]:
    """Rotate points around the unit vector u with the angle phi (radians).

    Args:
        points: list of points to be rotated
        u: normal vector of the rotation axis
        phi: rotation angle in radians

    Return:
        (list of rotated points, rotation matrix)

    """
    if length(u) < GEOM_EPSILON or abs(phi) < GEOM_EPSILON:
        # No need to rotate
        return points, np.ones((3, 3))

    # Rotate the points
    R = rotation_matrix(u, phi)

    # Convert points to list of Points
    rotated_points = rotate_points(points, R)

    return rotated_points, R


def rotate_points_to_plane(
    points: list[Point], anchor: Point, u: np.ndarray, d: float = 0.0
) -> tuple[list[Point], np.ndarray, float]:
    """Rotate and translate points to a plane defined by a normal vec. and dist. from origin d.

    If anchor is not Point(0.0, 0.0, 0.0) and d is not 0.0, then points are also translated!

    Args:
        points: list of points to be rotated
        anchor: rotation center point
        u: normal vector of the new plane (rotation)
        d: distance from origin (0,0,0) of the new plane (translation) (default 0.0)

    Return:
        (list of rotated points, rotation axis, rotation angle)
    """

    # Find normal to the points
    p_norm = normal(points[-1], points[0], points[1])

    # Convert to array
    pts_arr = np.array([p.vector() for p in points])

    # Move points to anchor
    if anchor != Point(0.0, 0.0, 0.0):
        pts_arr -= anchor.vector()

    # Find rotation axis
    rotaxis = np.cross(p_norm, u)
    if (np.abs(rotaxis) < GEOM_EPSILON).all():
        # No need to rotate, the points are already at the correct plane
        phi = 0.0
        return points, rotaxis, phi

    rotaxis /= np.linalg.norm(rotaxis)

    # Find rotation angle
    phi = angle(p_norm, u)

    # Rotate the points
    R = rotation_matrix(rotaxis, phi)
    pts_arr = pts_arr.dot(R.T)

    # Move points back from anchor
    if anchor != Point(0.0, 0.0, 0.0):
        pts_arr += anchor.vector()

    # Move points to d (translation)
    p_dest = u * d
    pts_arr += p_dest

    rot_and_trans_pts = [Point(x, y, z) for (x, y, z) in pts_arr]

    return rot_and_trans_pts, rotaxis, phi
