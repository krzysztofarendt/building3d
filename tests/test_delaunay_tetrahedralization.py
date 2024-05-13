import numpy as np
import pytest

from building3d import random_id
from building3d.geom.cloud import are_points_coplanar
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.tetrahedron import tetrahedron_volume
from building3d.geom.wall import Wall
from building3d.mesh.exceptions import MeshError
from building3d.mesh.tetrahedralization import delaunay_tetrahedralization
from building3d.mesh.triangulation import delaunay_triangulation


def test_tetrahedralization():
    delta = 1.0

    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 0.5)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.5)

    floor_id = random_id()
    wall0_id = random_id()
    wall1_id = random_id()
    wall2_id = random_id()
    wall3_id = random_id()
    roof_id = random_id()

    floor = Polygon([p0, p3, p2, p1], name=floor_id)
    wall0 = Polygon([p0, p1, p5, p4], name=wall0_id)
    wall1 = Polygon([p1, p2, p6, p5], name=wall1_id)
    wall2 = Polygon([p3, p7, p6, p2], name=wall2_id)
    wall3 = Polygon([p0, p4, p7, p3], name=wall3_id)
    roof = Polygon([p4, p5, p6, p7], name=roof_id)
    walls = Wall([floor, wall0, wall1, wall2, wall3, roof])

    floor_vertices, _ = delaunay_triangulation(floor)
    wall0_vertices, _ = delaunay_triangulation(wall0)
    wall1_vertices, _ = delaunay_triangulation(wall1)
    wall2_vertices, _ = delaunay_triangulation(wall2)
    wall3_vertices, _ = delaunay_triangulation(wall3)
    roof_vertices, _ = delaunay_triangulation(roof)
    solid = Solid([walls])

    # If delta is too big, the solid mesh cannot be generated
    with pytest.raises(MeshError):
        vertices, tetrahedra = delaunay_tetrahedralization(
            sld=solid,
            boundary_vmap={
                floor_id: floor_vertices,
                wall0_id: wall0_vertices,
                wall1_id: wall1_vertices,
                wall2_id: wall2_vertices,
                wall3_id: wall3_vertices,
                roof_id: roof_vertices,
            },
            delta=delta,
        )

    # If delta is small enough, the number of returned vertices will be larger
    # than polygon mesh vertices
    delta = 0.25
    vertices, tetrahedra = delaunay_tetrahedralization(
        sld=solid,
        boundary_vmap={
            floor_id: floor_vertices,
            wall0_id: wall0_vertices,
            wall1_id: wall1_vertices,
            wall2_id: wall2_vertices,
            wall3_id: wall3_vertices,
            roof_id: roof_vertices,
        },
        delta=delta,
    )

    assert len(np.unique(tetrahedra)) == len(
        vertices
    ), "More points used in tetrahedra than available vertices"
    assert (
        np.max(np.array(tetrahedra)) == len(vertices) - 1
    ), "Not all vertices used in the solid mesh"

    # Make sure points are not duplicated
    for i in range(len(vertices) - 1):
        for j in range(i + 1, len(vertices)):
            assert vertices[i] != vertices[j]

    # boundary_vertices = (
    #     floor_vertices
    #     + wall0_vertices
    #     + wall1_vertices
    #     + wall2_vertices
    #     + wall3_vertices
    #     + roof_vertices
    # )
    # assert len(vertices) > len(boundary_vertices)  # TODO: Can be removed? This does not have to be always True

    # Assert tetrahedra have non-zero volume
    for i, el in enumerate(tetrahedra):
        p0 = vertices[el[0]]
        p1 = vertices[el[1]]
        p2 = vertices[el[2]]
        p3 = vertices[el[3]]
        vol = tetrahedron_volume(p0, p1, p2, p3)
        ref_volume = tetrahedron_volume(
            Point(0.0, 0.0, 0.0),
            Point(delta, 0.0, 0.0),
            Point(0.0, delta, 0.0),
            Point(0.0, 0.0, delta),
        )
        min_volume = ref_volume / 50.0
        assert vol > min_volume, f"Volume[{i}]={vol} < minimum ({min_volume})"

        # Assert tetrahedra vertices are not coplanar
        assert not are_points_coplanar(p0, p1, p2, p3)
