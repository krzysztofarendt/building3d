import logging

import numpy as np

from building3d.geom.point import Point
from building3d.geom.tetrahedron import tetrahedron_volume
from building3d.geom.triangle import triangle_area
from building3d.geom.vector import length
from building3d.geom.vector import vector


logger = logging.getLogger(__name__)


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
