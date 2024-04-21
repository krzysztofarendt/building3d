import copy
import logging

import numpy as np

from building3d.geom.point import Point
from building3d.geom.tetrahedron import tetrahedron_volume
from building3d.config import MESH_DELTA


logger = logging.getLogger(__name__)


def minimum_triangle_area(delta: float = MESH_DELTA) -> float:
    """Calculate min. face area for PolyMesh quality assurance."""
    return delta ** 2 / 10.0


def minimum_tetra_volume(delta: float = MESH_DELTA) -> float:
    """Calculate minimum tetrahedron volume for mesh quality assurance."""
    ref_volume = tetrahedron_volume(
        Point(0.0, 0.0, 0.0),
        Point(delta, 0.0, 0.0),
        Point(0.0, delta, 0.0),
        Point(0.0, 0.0, delta),
    )
    min_vol= ref_volume / 50.
    return min_vol


def collapse_points(
    vertices: list[Point],
    elements: list[list[int]],
) -> tuple[list[Point], list[list[int]]]:
    """Merge overlapping points.

    Checks if there are points which are equal to one another.
    Point equality is defined in the Point class. In general,
    points are equal if the difference between their coordinates is below
    the defined epsilon.

    Subsequently, overlapping points are merged.

    Overlapping points exist for example on the edges of adjacent polygons,
    because the polygon meshes are generated independently.

    Args:
        vertices: list of points
        elements: list of faces/tetrahedra

    Return:
        tuple of modified list of points and list of elements
    """
    logger.debug("Collapsing points...")
    logger.debug(f"Number of points before collapsing: {len(vertices)}")

    # Identify identical points
    same_points = {}
    for i, p in enumerate(vertices):
        if p in same_points.keys():
            same_points[p].append(i)
        else:
            same_points[p] = [i]

    # Merge same points
    for_deletion = set()

    for i in range(len(vertices)):
        p = vertices[i]
        p_to_keep = same_points[p][0]
        for j in range(1, len(same_points[p])):
            p_to_delete = same_points[p][j]
            for_deletion.add(p_to_delete)

            # Replace point to be deleted with the one to keep in each face
            for k in range(len(elements)):
                if p_to_delete in elements[k]:
                    elements[k] = \
                        [x if x != p_to_delete else p_to_keep for x in elements[k]]

    # Reindex
    for_deletion = sorted(list(for_deletion), reverse=True)
    for p_to_delete in for_deletion:
        for k in range(len(elements)):
            elements[k] = [x - 1 if x > p_to_delete else x for x in elements[k]]
        vertices.pop(p_to_delete)

    logger.debug(f"Number of points after collapsing: {len(vertices)}")
    return vertices, elements


def purge_mesh(
    vertices: list[Point],
    elements: list[list[int]],
) -> tuple[list[Point], list[list[int]]]:
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
            elements[k] = [x - 1 if x > p_to_delete else x for x in elements[k]]
        vertices.pop(p_to_delete)

    return vertices, elements
