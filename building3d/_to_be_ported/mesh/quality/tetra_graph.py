import numpy as np
from numba import njit

from building3d.geom.point import Point
from building3d.geom.cloud import points_to_array
from building3d.config import GEOM_ATOL


def find_neighbors(
    vertices: list[Point], elements: list[tuple[int, ...]]
) -> list[list[int]]:
    """Find neighboring elements (facing one another).

    Returns a list of neighbors, e.g. `neighbors[3] = [5, 7, 9]` means
    that element number 3 has 3 adjacent elements: 5, 7, 9.

    Neighboring elements (tetrahedra) are the ones that share 3 vertices.
    """
    neighbors = [[] for _ in range(len(elements))]
    for i in range(len(elements) - 1):
        for j in range(i + 1, len(elements)):
            # Elements facing each other if they share 3 vertices
            el1 = elements[i]
            el2 = elements[j]
            el1_pts = set([vertices[el1[x]] for x in range(4)])
            el2_pts = set([vertices[el2[x]] for x in range(4)])
            num_shared = len(el1_pts.intersection(el2_pts))
            if num_shared == 3:
                neighbors[i].append(j)
                neighbors[j].append(i)
    return neighbors


def find_neighbors_numba_wrap(
    vertices: list[Point], elements: list[tuple[int, ...]]
) -> list[list[int]]:
    """Wrapper for the numba equivalent which fixes the input/output data types."""
    neighbors_arr = find_neighbors_numba(
        vertices=points_to_array(vertices),
        elements=np.array(elements),
        epsilon=GEOM_ATOL,
    )
    neighbors = []
    for ngb in neighbors_arr:
        neighbors.append([x for x in ngb if x > -1])
    return neighbors


@njit
def find_neighbors_numba(
    vertices: np.ndarray, elements: np.ndarray, epsilon: float
) -> np.ndarray:
    """Numba equivalent of find_neighbors().

    The returned array has shape (len(elements), 4).
    If an element has less than 4 neighbors, then free slots
    will be filled with -1.
    """
    neighbors = np.full((len(elements), 4), -1)

    for i in range(len(elements) - 1):
        for j in range(i + 1, len(elements)):
            # Elements facing each other if they share 3 vertices
            el1 = elements[i]
            el2 = elements[j]
            el1_pts = np.zeros((4, 3))  # 4 points, each with 3 coordinates
            el2_pts = np.zeros((4, 3))
            for k in range(4):
                el1_pts[k, :] = vertices[el1[k], :]
                el2_pts[k, :] = vertices[el2[k], :]
            num_shared = 0
            for p1 in el1_pts:
                for p2 in el2_pts:
                    if (
                        (np.abs(p1[0] - p2[0]) < epsilon)
                        and (np.abs(p1[1] - p2[1]) < epsilon)
                        and (np.abs(p1[2] - p2[2]) < epsilon)
                    ):
                        num_shared += 1
            if num_shared == 3:
                for k in range(4):
                    if neighbors[i][k] == -1:
                        neighbors[i][k] = j
                        break
                for k in range(4):
                    if neighbors[j][k] == -1:
                        neighbors[j][k] = i
                        break

    return neighbors
