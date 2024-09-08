import copy
import logging

import numpy as np

from building3d.geom.point import Point


logger = logging.getLogger(__name__)


def purge_mesh(
    vertices: list[Point],
    elements: list[tuple[int, ...]],
) -> tuple[list[Point], list[tuple]]:
    """Remove vertices not used in elements and reindex elements."""

    # Copy input lists (to not alter in place)
    vertices = [p for p in vertices]
    elements = copy.deepcopy(elements)

    # Find unused vertices
    unique = np.unique(elements).tolist()
    indices = [i for i in range(len(vertices))]
    to_delete = [i for i in indices if i not in unique]

    # Reindex
    to_delete = sorted(list(to_delete), reverse=True)
    for p_to_delete in to_delete:
        for k in range(len(elements)):
            elements[k] = tuple([x - 1 if x > p_to_delete else x for x in elements[k]])
        vertices.pop(p_to_delete)

    return vertices, elements
