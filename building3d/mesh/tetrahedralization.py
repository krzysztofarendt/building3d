from __future__ import annotations  # Needed for type hints to work (due to circular import)
from collections import defaultdict
import logging
import time

import numpy as np
from scipy.spatial import Delaunay

from building3d.mesh.exceptions import MeshError
from building3d.geom.point import Point
from building3d.geom.solid import Solid
from building3d.geom.tetrahedron import tetrahedron_volume
from building3d.mesh.quality import minimum_tetra_volume
from building3d.mesh.quality import purge_mesh
from building3d.geom.tetrahedron import tetrahedron_centroid
from building3d.mesh.triangulation import delaunay_triangulation
from building3d import random_within
from building3d.config import MESH_JOGGLE
from building3d.config import MESH_DELTA
from building3d.geom.plane import are_points_coplanar


logger = logging.getLogger(__name__)


def imbalance(vols):
    return max(vols) / min(vols)


def recalc_selected_volumes(volumes, keys, vertices, elements):
    for i in keys:
        p0 = vertices[elements[i][0]]
        p1 = vertices[elements[i][1]]
        p2 = vertices[elements[i][2]]
        p3 = vertices[elements[i][3]]
        volumes[i] = tetrahedron_volume(p0, p1, p2, p3)
    return volumes


def get_invalid_points(vertices, tetrahedra, restricted):
    invalid = []
    # Create a map {vertex number: list of element indices}
    vertex_to_elems = defaultdict(list)
    for i, el in enumerate(tetrahedra):
        for vertex_index in el:
            vertex_to_elems[vertex_index].append(i)
    for i in range(len(vertices)):
        if i in restricted:
            continue
        # Calculate element volumes
        volumes = recalc_selected_volumes(
            volumes={},
            keys=[x for x in range(len(tetrahedra))],
            vertices=vertices,
            elements=tetrahedra,
        )
        # Find connected elements
        connected_elements = vertex_to_elems[i]
        # Find their volumes
        connected_volumes = [volumes[x] for x in connected_elements]
        # If imbalance too high, move the vertex to minimize imbalance
        imbalance_threshold = 1000.
        if imbalance(connected_volumes) > imbalance_threshold:
            invalid.append(i)

    return invalid



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
        for poly in sld.polygons():
            polymesh_vertices, _ = delaunay_triangulation(poly, delta=delta)
            for pt in polymesh_vertices:
                if pt not in vertices:
                    vertices.append(pt)
                    boundary_pts.add(pt)
    else:
        logger.debug("Will take boundary vertices provided by the user")
        for _, poly_points in boundary_vertices.items():
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
                # Check if point is inside solid
                if sld.is_point_inside(pt):
                    # Check if point is closer to boundary than already existing points
                    distance_to_boundary_ok = True
                    for poly in sld.polygons():
                        if poly.distance_point_to_polygon(pt) < delta / 2:
                            # It is too close to at least one polygon, points should not be used
                            distance_to_boundary_ok = False
                            break
                    if distance_to_boundary_ok:
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
        # raise MeshError("Not all vertices have been used for mesh. Does this ever happen?")
        pass

    # logger.debug("Attempting to remove points attached to invalid elements (before second pass)")
    # boundary_pts_indices = [i for i, p in enumerate(vertices) if p in boundary_pts]
    # invalid_vertices = get_invalid_points(vertices, tetrahedra, boundary_pts_indices)
    # vertices = [vertices[i] for i in range(len(vertices)) if i not in invalid_vertices]

    # pts_arr = np.array([[p.x, p.y, p.z] for p in vertices])
    # logger.debug(f"Delaunay tetrahedralization (second pass) on point array with shape {pts_arr.shape}")
    # delaunay = Delaunay(pts_arr, qhull_options="Qt", incremental=False)
    # tetrahedra = delaunay.simplices
    # logger.debug(f"Number of resulting mesh tetrahedra in {sld.name} = {len(tetrahedra)}")

    logger.debug("Attempting to find and remove elements with invalid geometry or position...")
    tetrahedra_ok = []
    for el in tetrahedra:
        p0 = vertices[el[0]]
        p1 = vertices[el[1]]
        p2 = vertices[el[2]]
        p3 = vertices[el[3]]
        vol = tetrahedron_volume(p0, p1, p2, p3)
        volume_ok = vol > min_volume
        if volume_ok:
            coplanar = are_points_coplanar(p0, p1, p2, p3)
            if not coplanar:
                if (
                        (p0 in boundary_pts) and \
                        (p1 in boundary_pts) and \
                        (p2 in boundary_pts) and \
                        (p3 in boundary_pts)
                ):
                    # Need to check if the centroid is  inside the solid
                    # (if it is not, this is a concave edge/corner)
                    ctr = tetrahedron_centroid(p0, p1, p2, p3)
                    point_is_inside = sld.is_point_inside(ctr)
                    if point_is_inside:
                        tetrahedra_ok.append(el)
                else:
                    # At least one of vert. is not at the boundary, so it must be el. inside the solid
                    tetrahedra_ok.append(el)

    if len(tetrahedra) != len(tetrahedra_ok):
        logger.debug(f"Purging mesh...")
        vertices, tetrahedra = purge_mesh(vertices, tetrahedra_ok)
    else:
        tetrahedra = tetrahedra_ok

    logger.debug(f"Number of tetrahedra with correct shape = {len(tetrahedra_ok)}")
    logger.debug(f"Final number of tetrahedra in {sld.name} = {len(tetrahedra)}")
    logger.debug(f"Final number of vertices used in mesh {sld.name} = {len(np.unique(tetrahedra))}")
    logger.debug(f"Final number of all vertices in {sld.name} = {len(vertices)}")

    # Sanity checks
    unique_indices = np.unique(tetrahedra)
    assert len(unique_indices) == len(vertices), "Not all vertices have been used for mesh!"

    for pt in sld.vertices():
        assert pt in vertices, f"Solid point missing: {pt}"

    return vertices, tetrahedra
