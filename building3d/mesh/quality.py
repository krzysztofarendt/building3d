import copy
import logging

import numpy as np

from building3d.geom.point import Point
from building3d.geom.tetrahedron import tetrahedron_volume
from building3d.geom.triangle import triangle_area
from building3d.geom.vector import length
from building3d.geom.vector import vector
from building3d.config import MESH_DELTA


logger = logging.getLogger(__name__)


def minimum_triangle_area(delta: float = MESH_DELTA) -> float:
    """Calculate min. face area for PolyMesh quality assurance."""
    return delta ** 2 / 50.0


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


def total_volume(vertices: list[Point], elements: list[list[int]]) -> float:
    """Return the sum of volumes of all mesh tetrahedra."""
    tot_vol = 0
    for el in elements:
        p0 = vertices[el[0]]
        p1 = vertices[el[1]]
        p2 = vertices[el[2]]
        p3 = vertices[el[3]]
        tot_vol += tetrahedron_volume(p0, p1, p2, p3)

    return tot_vol


def mesh_stats(vertices: list[Point], elements: list[list[int]]) -> str:
    """Return a string with mesh statistics. Works with PolyMesh and SolidMesh."""

    is_surface_mesh = False
    is_volume_mesh = False

    if len(elements[0]) == 3:
        is_surface_mesh = True
    elif len(elements[0]) == 4:
        is_volume_mesh = True

    if is_surface_mesh:
        num_of_vertices = len(vertices)
        num_of_faces = len(elements)

        face_areas = []
        edge_lengths = []
        for i in range(num_of_faces):
            p0 = vertices[elements[i][0]]
            p1 = vertices[elements[i][1]]
            p2 = vertices[elements[i][2]]
            face_areas.append(triangle_area(p0, p1, p2))
            edge_lengths.append(length(vector(p0, p1)))
            edge_lengths.append(length(vector(p1, p2)))
            edge_lengths.append(length(vector(p2, p0)))

        max_face_area = np.max(face_areas)
        avg_face_area = np.mean(face_areas)
        min_face_area = np.min(face_areas)
        max_edge_len = np.max(edge_lengths)
        avg_edge_len = np.mean(edge_lengths)
        min_edge_len = np.min(edge_lengths)

        area_hist, bin_edges = np.histogram(face_areas, bins=10)

        stats = "PolyMesh statistics:\n"
        stats += "====================\n"
        stats += f"\t{num_of_vertices=}\n"
        stats += f"\t{num_of_faces=}\n"
        stats += f"\t{max_face_area=}\n"
        stats += f"\t{avg_face_area=}\n"
        stats += f"\t{min_face_area=}\n"
        stats += f"\t{max_edge_len=}\n"
        stats += f"\t{avg_edge_len=}\n"
        stats += f"\t{min_edge_len=}\n"
        stats += "\tArea distribution:\n"
        for i in range(len(area_hist)):
            bracket = ")" if i < len(area_hist) - 1 else "]"
            stats += f"\t- [{bin_edges[i]:.3f}, {bin_edges[i+1]:.3f}{bracket} = {area_hist[i]}\n"

        return stats

    elif is_volume_mesh:
        if len(elements) == 0:
            return "SolidMesh empty!"

        volumes = []
        for el in elements:
            p0 = vertices[el[0]]
            p1 = vertices[el[1]]
            p2 = vertices[el[2]]
            p3 = vertices[el[3]]
            vol = tetrahedron_volume(p0, p1, p2, p3)
            volumes.append(vol)

        vol_hist, bin_edges = np.histogram(volumes, bins=10)

        num_of_vertices = len(vertices)
        num_of_elements = len(elements)
        max_element_volume = max(volumes)
        avg_element_volume = np.mean(volumes)
        min_element_volume = min(volumes)

        stats = "SolidMesh statistics:\n"
        stats += "=====================\n"
        stats += f"\tnum_of_vertices={num_of_vertices}\n"
        stats += f"\tnum_of_elements={num_of_elements}\n"
        stats += f"\tmax_element_volume={max_element_volume}\n"
        stats += f"\tavg_element_volume={avg_element_volume}\n"
        stats += f"\tmin_element_volume={min_element_volume}\n"
        stats += "\tVolume distribution:\n"
        for i in range(len(vol_hist)):
            bracket = ")" if i < len(vol_hist) - 1 else "]"
            stats += f"\t- [{bin_edges[i]:.3f}, {bin_edges[i+1]:.3f}{bracket} = {vol_hist[i]}\n"
        return stats

    else:
        msg = f"Mesh format unknown. Elements contain {len(elements[0])} vertices."
        logger.error(msg)
        return msg
