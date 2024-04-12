from __future__ import annotations  # Needed for type hints to work (due to circular import)
import logging

import numpy as np
from scipy.spatial import Delaunay

from ..geom.exceptions import GeometryError
from ..geom.point import Point
from ..geom.solid import Solid
from ..geom.tetrahedron import tetrahedron_volume


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
    vertices = []

    min_volume = delta ** 3 / 50.0
    logger.debug(f"Assuming tetrahedron min. volume = {min_volume}")

    # Collect meshes from the boundary polygons
    # -> boundary_vertices, boundary_faces
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
    tri = Delaunay(pts_arr, qhull_options="Qt", incremental=False)
    tetrahedra = tri.simplices

    # Remove tetrahedra with zero volume
    removed_el = []
    for i, el in enumerate(tetrahedra):
        p0 = vertices[el[0]]
        p1 = vertices[el[1]]
        p2 = vertices[el[2]]
        p3 = vertices[el[3]]
        vol = tetrahedron_volume(p0, p1, p2, p3)
        if vol < min_volume:
            removed_el.append(i)
    tetrahedra = [el for i, el in enumerate(tetrahedra) if i not in removed_el]

    logger.debug(f"Number of mesh tetrahedra in {sld.name} = {len(tetrahedra)}")
    logger.debug(f"Number of mesh vertices in {sld.name} = {len(vertices)}")

    # SANITY CHECKS
    # Make sure all boundary vertices are in the final_vertices
    # and that the number of returned vertices is higher than the sum of polygon mesh vertices
    unique_boundary_vertices = []

    unique_points = [vertices[i] for i in np.unique(np.array(tetrahedra))]
    assert len(unique_points) == len(vertices), "Not all points unique"

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
