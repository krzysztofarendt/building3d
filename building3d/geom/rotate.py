import numpy as np

from .point import Point
from .vector import angle


def rotation_matrix(u: np.ndarray, phi: float) -> np.ndarray:
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
    W = np.array([[0, -u[2], u[1]],
                  [u[2], 0, -u[0]],
                  [-u[1], u[0], 0]])
    R = np.eye(3) + np.sin(phi) * W + (2 * np.sin(phi/2) ** 2) * np.dot(W, W)

    return R


def rotate_points_around_vector(
    points: list[Point], u: np.ndarray, phi: float
) -> list[Point]:

    # Convert points to array
    pts_arr = np.array([p.vector() for p in points])

    # Rotate the points
    R = rotation_matrix(u, phi)
    pts_arr = pts_arr.dot(R.T)

    # Convert points to list of Points
    rotated_points = [Point(x, y, z) for (x, y, z) in pts_arr]

    return rotated_points


def rotate_points_to_plane(
    points: list[Point], anchor: Point, normal: np.ndarray, d: float,
) -> list[Point]:

    # Find normal to the points
    vec1 = points[1].vector() - points[0].vector()
    vec2 = points[-1].vector() - points[0].vector()
    p_norm = np.cross(vec1, vec2)
    p_norm /= np.linalg.norm(p_norm)

    # Move points to anchor
    pts_arr = np.array([p.vector() for p in points])
    pts_arr -= anchor.vector()

    # Find rotation axis
    u = np.cross(p_norm, normal)

    # Find rotation angle
    phi = angle(p_norm, normal)

    # Rotate the points
    R = rotation_matrix(u, phi)
    pts_arr = pts_arr.dot(R.T)

    # Move points back from anchor
    pts_arr += anchor.vector()

    # Move points to d
    p_dest = normal * d
    pts_arr += p_dest

    rot_and_trans_pts = [Point(x, y, z) for (x, y, z) in pts_arr]

    return rot_and_trans_pts
