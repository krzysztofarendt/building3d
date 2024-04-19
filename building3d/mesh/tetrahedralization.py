from __future__ import annotations  # Needed for type hints to work (due to circular import)
import logging

import numpy as np
from scipy.spatial import Delaunay

from building3d.mesh.exceptions import MeshError
from building3d.geom.point import Point
from building3d.geom.solid import Solid
from building3d.geom.tetrahedron import tetrahedron_volume
from building3d.geom.tetrahedron import minimum_tetra_volume
from building3d.geom.tetrahedron import tetrahedron_centroid
from building3d.mesh.delaunay_triangulation import delaunay_triangulation
from building3d import random_within
from building3d.config import MESH_JOGGLE
from building3d.config import MESH_DELTA
from building3d.geom.plane import are_points_coplanar


logger = logging.getLogger(__name__)


def delaunay_tetrahedralization(
    sld: Solid,
    boundary_vertices: dict[str, list[Point]],
    delta: float = MESH_DELTA,
) -> tuple[list[Point], list[list[int]]]:
    """Constrained Delaunay tetrahedralization of a solid.

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
    boundary_pts = set()

    min_volume = minimum_tetra_volume(delta)
    logger.debug(f"Assuming tetrahedron min. volume = {min_volume}")

    # Collect meshes from the boundary polygons
    # -> boundary_vertices, boundary_faces
    if len(boundary_vertices.keys()) == 0:
        logger.debug("Need to create boundary mesh to get vertices at the surrounding polygons")
        for poly in sld.boundary:
            polymesh_vertices, _ = delaunay_triangulation(poly, delta=delta)
            for pt in polymesh_vertices:
                if pt not in vertices:
                    vertices.append(pt)
                    boundary_pts.add(pt)
    else:
        logger.debug("Will take boundary vertices provided by the user")
        for poly_name, poly_points in boundary_vertices.items():
            for pt in poly_points:
                # Do not add duplicate points
                if pt not in vertices:
                    vertices.append(pt)
                    boundary_pts.add(pt)

    logger.debug("Add new points inside the solid")
    bbox_pmin, bbox_pmax = sld.bounding_box()
    xmin = bbox_pmin.x
    ymin = bbox_pmin.y
    zmin = bbox_pmin.z
    xmax = bbox_pmax.x
    ymax = bbox_pmax.y
    zmax = bbox_pmax.z

    # Make sure delta smaller than bbox dimensions
    if delta >= xmax - xmin or delta >= ymax - ymin or delta >= zmax - zmin:
        raise MeshError(f"Solid {sld.name} cannot be meshed due to too large delta ({delta})")

    xgrid = np.arange(xmin + delta, xmax, delta)
    ygrid = np.arange(ymin + delta, ymax, delta)
    zgrid = np.arange(zmin + delta, zmax, delta)
    for x in xgrid:
        for y in ygrid:
            for z in zgrid:
                pt = Point(
                    x + random_within(MESH_JOGGLE * delta),
                    y + random_within(MESH_JOGGLE * delta),
                    z + random_within(MESH_JOGGLE * delta),
                )
                # TODO: Below code is very slow -> need to optimize
                #       poly.distance_point_to_polygon can be replaced with "thick" polygons
                #       i.e. making solids from the polygons and checking if the point
                #       is inside this solid (which should be faster)
                if sld.is_point_inside(pt):
                    far_enough_from_boundary = True
                    for poly in sld.boundary:
                        if poly.distance_point_to_polygon(pt) < delta / 2:
                            far_enough_from_boundary = False
                            break
                    if far_enough_from_boundary is True:
                        vertices.append(pt)

    # Delaunary - first pass
    pts_arr = np.array([[p.x, p.y, p.z] for p in vertices])
    logger.debug(f"Delaunay tetrahedralization (first pass) on point array with shape {pts_arr.shape}")
    delaunay = Delaunay(pts_arr, qhull_options="Qt", incremental=False)
    tetrahedra = delaunay.simplices
    logger.debug(f"Number of resulting mesh tetrahedra in {sld.name} = {len(tetrahedra)}")

    # Remove unused points and tetrahedra with small volume
    unique_indices = np.unique(tetrahedra)

    if len(unique_indices) == len(vertices):
        logger.debug("All vertices have been used. Great!")
    else:
        raise MeshError("Not all vertices have been used for mesh. Does this ever happen?")

    logger.debug("Attempting to find and remove elements with invalid geometry or position...")
    tetrahedra_ok = []
    for el in tetrahedra:
        p0 = vertices[el[0]]
        p1 = vertices[el[1]]
        p2 = vertices[el[2]]
        p3 = vertices[el[3]]
        coplanar = are_points_coplanar(p0, p1, p2, p3)
        vol = tetrahedron_volume(p0, p1, p2, p3)
        ctr = tetrahedron_centroid(p0, p1, p2, p3)
        if not coplanar and vol > min_volume:
            if sld.is_point_inside(ctr):
                tetrahedra_ok.append(el)

    logger.debug(f"Number of tetrahedra with correct shape = {len(tetrahedra_ok)}")
    tetrahedra = tetrahedra_ok

    logger.debug(f"Final number of tetrahedra in {sld.name} = {len(tetrahedra)}")
    logger.debug(f"Final number of vertices used in mesh {sld.name} = {len(np.unique(tetrahedra))}")
    logger.debug(f"Final number of all vertices in {sld.name} = {len(vertices)}")

    # Sanity checks
    unique_indices = np.unique(tetrahedra)
    assert len(unique_indices) == len(vertices), "Not all vertices have been used for mesh!"

    for pt in boundary_pts:
        assert pt in vertices, f"Boundary point missing: {pt}"

    return vertices, tetrahedra
