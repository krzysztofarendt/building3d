import numpy as np

from building3d.geom.point import Point
from .tetra_graph import find_neighbors_numba_wrap


def count_tetra_neighbors(
    vertices: list[Point], elements: list[tuple[int, ...]]
) -> np.ndarray:
    """Count the number of neighbors for each mesh (tetrahedral) element.

    Args:
        vertices: mesh points
        elements: list of tetrahedra

    Return:
        array with the number of neighbors for each element, shape (num_elements, )
    """
    # Find all neighboring elements
    neighbors = find_neighbors_numba_wrap(
        vertices=vertices,
        elements=elements,
    )

    # Count neighboring elements
    count = np.array([len(ngbs) for ngbs in neighbors], dtype=np.int32)

    return count
