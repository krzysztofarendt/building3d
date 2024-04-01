from __future__ import annotations  # Needed for type hints to work (due to circular import)

import numpy as np
from scipy.spatial import Delaunay

from ..geom.exceptions import GeometryError
from ..geom.point import Point
from ..geom.solid import Solid


def delaunay_tetrahedralization(
    sld: Solid,
    boundary_vertices: dict[str, list[Point]],
    delta: float = 0.5,
    init_vertices: None | list[Point] = None,
) -> tuple[list[Point], list[list[int]]]:
    """Delaunay tetrahedralization of a solid.

    Args:
        sld: solid to be meshed
        boundary_vertices: dict with polygon names and respective mesh vertices
        delta: approximate mesh size
        init_vertices: initial vertices to be used for tetrahedralization

    Return:
        (list of mesh points, list of tetrahedral elements)
    """
    vertices = []

    if init_vertices is not None:
        pass  # TODO: Add logic for init_vertices in solid_mesh.py (to be used for mesh refinement)
    else:
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

        xgrid = np.arange(xmin, xmax, delta)
        ygrid = np.arange(ymin, ymax, delta)
        zgrid = np.arange(zmin, zmax, delta)
        for x in xgrid:
            for y in ygrid:
                for z in zgrid:
                    pt = Point(x, y, z)
                    if sld.is_point_inside(pt):
                        if pt not in vertices:
                            vertices.append(pt)

    # Tetrahedralization - first pass
    pts_arr = np.array([[p.x, p.y, p.z] for p in vertices])
    tri = Delaunay(pts_arr, incremental=False)
    tetrahedra = tri.simplices

    # Remove points not used in the tetrahedralization
    unique_tetra_indices = np.unique(tetrahedra)
    final_vertices = []
    for i, p in enumerate(vertices):
        if i in unique_tetra_indices:
            final_vertices.append(p)

    # Tetrahedralization - second pass (TODO: can it be done in a single pass?)
    pts_arr = np.array([[p.x, p.y, p.z] for p in final_vertices])
    tri = Delaunay(pts_arr, incremental=False)
    tetrahedra = tri.simplices
    assert len(np.unique(tetrahedra)) == len(final_vertices)

    # Make sure all boundary vertices are in the final_vertices
    # and that the number of returned vertices is higher than the sum of polygon mesh vertices
    num_of_boundary_vertices = 0
    for poly_name, poly_points in boundary_vertices.items():
        for pt in poly_points:
            num_of_boundary_vertices += 1
            assert pt in final_vertices, \
                f"{pt} (from mesh of {poly_name} polygon) not in the solid mesh"

    assert len(final_vertices) > num_of_boundary_vertices, \
        "Solid mesh has less vertices than boundary mesh"

    # Prepare outputs
    elements = tetrahedra.tolist()
    vertices = final_vertices

    assert np.max(np.array(elements)) == len(vertices) - 1, \
        "Number of vertices is different than max index used in tetrahedra"

    return vertices, elements
