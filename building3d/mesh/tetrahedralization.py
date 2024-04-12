from __future__ import annotations  # Needed for type hints to work (due to circular import)
import logging

import numpy as np
from scipy.spatial import Delaunay

from ..geom.exceptions import GeometryError
from ..geom.point import Point
from ..geom.solid import Solid
from ..geom.tetrahedron import tetrahedron_volume
from building3d.mesh.exceptions import MeshError
from building3d.mesh.triangulation import delaunay_triangulation

logger = logging.getLogger(__name__)


def delaunay_tetrahedralization(
    sld: Solid,
    boundary_vertices: dict[str, list[Point]],
    delta: float = 0.5,
) -> tuple[list[Point], list[list[int]]]:
    """Delaunay tetrahedralization of a solid.

    Args:
        sld: solid to be meshed
        boundary_vertices: dict with polygon names and respective mesh vertices
        delta: approximate mesh size

    Return:
        (list of mesh points, list of tetrahedral tetrahedra)
    """
    logger.debug(f"Starting tetrahedralization of {sld} with {delta=}")
    logger.debug(f"Number of polygons passed in boundary_vertices = {len(boundary_vertices.keys())}")
    for name in boundary_vertices:
        logger.debug(f"boundary vertifces for {name} = {len(boundary_vertices[name])}")

    vertices = []

    min_volume = delta ** 3 / 50.0
    logger.debug(f"Assuming tetrahedron min. volume = {min_volume}")

    # Collect meshes from the boundary polygons
    # -> boundary_vertices, boundary_faces
    if len(boundary_vertices.keys()) == 0:
        # Need to create boundary mesh to get vertices at the surrounding polygons
        for poly in sld.boundary:
            polymesh_vertices, _ = delaunay_triangulation(poly, delta=delta)
            for pt in polymesh_vertices:
                if pt not in vertices:
                    vertices.append(pt)
    else:
        # Will take boundary vertices provided by the user
        for poly_name, poly_points in boundary_vertices.items():
            for pt in poly_points:
                # Do not add duplicate points
                if pt not in vertices:
                    vertices.append(pt)

    # Add new points inside the solid
    bbox_pmin, bbox_pmax = sld.bounding_box()
    xmin = bbox_pmin.x
    ymin = bbox_pmin.y
    zmin = bbox_pmin.z
    xmax = bbox_pmax.x
    ymax = bbox_pmax.y
    zmax = bbox_pmax.z

    # Make sure delta smaller than bbox dimensions
    if delta >= xmax - xmin or delta >= ymax - ymin or delta >= zmax - zmin:
        raise GeometryError(f"Solid {sld.name} cannot be meshed due to too large delta ({delta})")

    xgrid = np.arange(xmin + delta, xmax, delta)
    ygrid = np.arange(ymin + delta, ymax, delta)
    zgrid = np.arange(zmin + delta, zmax, delta)
    for x in xgrid:
        for y in ygrid:
            for z in zgrid:
                pt = Point(x, y, z)
                if sld.is_point_inside(pt):
                    if pt not in vertices:
                        vertices.append(pt)

    # Tetrahedralization - first pass
    pts_arr = np.array([[p.x, p.y, p.z] for p in vertices])
    logger.debug(f"Attempting Delaunay tetrahedralization on point array with shape {pts_arr.shape}")

    tri = Delaunay(pts_arr, qhull_options="Qt", incremental=False)
    tetrahedra = tri.simplices
    logger.debug(f"Number of mesh tetrahedra in {sld.name} = {len(tetrahedra)}")

    unique_points = [vertices[i] for i in np.unique(np.array(tetrahedra))]
    assert len(unique_points) == len(vertices), "Not all points used in tetrahedralization?"

    # Remove tetrahedra with zero volume
    removed_el = []
    for i, el in enumerate(tetrahedra):
        p0 = vertices[el[0]]
        p1 = vertices[el[1]]
        p2 = vertices[el[2]]
        p3 = vertices[el[3]]
        vol = tetrahedron_volume(p0, p1, p2, p3)
        if vol < min_volume:
            logger.warning(f"Tetrahedron {i} has too low volume ({vol}) and will be removed.")
            removed_el.append(i)
    logger.debug(f"Number of tetrahedra to be removed due to small volume = {len(removed_el)}")

    tetrahedra = [el for i, el in enumerate(tetrahedra) if i not in removed_el]

    # TODO: Reindexing vertices would be useful here, because not all may be used
    pass
    vertices, tetrahedra = collapse_points(vertices, tetrahedra)  # TODO: is it needed?

    logger.debug(f"Number of tetrahedra in {sld.name} = {len(tetrahedra)}")
    logger.debug(f"Number of mesh vertices in {sld.name} = {len(vertices)}")

    # SANITY CHECKS
    # Make sure all boundary vertices are in the final_vertices
    # and that the number of returned vertices is higher than the sum of polygon mesh vertices
    unique_boundary_vertices = []


    for poly_name, poly_points in boundary_vertices.items():
        for pt in poly_points:
            if pt not in unique_boundary_vertices:
                unique_boundary_vertices.append(pt)
            assert pt in vertices, \
                f"{pt} (from mesh of {poly_name} polygon) not in the solid mesh"
            assert pt in unique_points, "Not all points used for mesh vertices"

    assert len(vertices) > len(unique_boundary_vertices), \
        "Solid mesh has less vertices than boundary mesh"
    assert np.max(np.array(tetrahedra)) == len(vertices) - 1, \
        "Number of vertices is different than max index used in tetrahedra"

    return vertices, tetrahedra


def collapse_points(
        vertices: list[Point], elements: list[list[int]]
) -> tuple[list[Point], list[list[int]]]:
    """Merge overlapping points.
    """
    logger.debug("Collapsing points")
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
