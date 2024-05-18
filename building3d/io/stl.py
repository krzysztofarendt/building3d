"""STL import/export.

STL format:
---------------------------------------
solid name
     facet normal ni nj nk
         outer loop
             vertex v1x v1y v1z
             vertex v2x v2y v2z
             vertex v3x v3y v3z
         endloop
     endfacet
endsolid name
---------------------------------------

Used for:
- building3d.geom.solid.Zone
"""
from pathlib import Path

import numpy as np

import building3d.logger
from building3d import random_id
from building3d.config import GEOM_RTOL
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone
from building3d.display.plot_zone import plot_zone


def write_stl(path: str, zone: Zone) -> None:
    """Read STL file.

    STL does not contain information about how facets (triangles)
    are grouped together, so each facet is treated as a separate triangular wall/polygon.
    """
    lines = []
    l1 = " " * 2
    l2 = " " * 4
    l3 = " " * 6
    for sld_name, sld in zone.solids.items():
        lines.append(f"solid {sld_name}\n")
        for wall in sld.walls:
            for _, poly in wall.polygons.items():
                ni, nj, nk = poly.normal
                for facet in poly.triangles:
                    lines.append(f"{l1}facet normal {ni} {nj} {nk}\n")
                    lines.append(f"{l2}outer loop\n")
                    v1x, v1y, v1z = poly.points[facet[0]].vector()
                    v2x, v2y, v2z = poly.points[facet[1]].vector()
                    v3x, v3y, v3z = poly.points[facet[2]].vector()
                    lines.append(f"{l3}vertex {v1x} {v1y} {v1z}\n")
                    lines.append(f"{l3}vertex {v2x} {v2y} {v2z}\n")
                    lines.append(f"{l3}vertex {v3x} {v3y} {v3z}\n")
                    lines.append(f"{l2}endloop\n")
                    lines.append(f"{l1}endfacet\n")
        lines.append(f"endsolid {sld.name}\n")
    with open(path, "w") as f:
        f.writelines(lines)


def read_stl(path: str) -> Zone:

    zone = Zone(name=Path(path).stem)
    with open(path, "r") as f:
        lines = f.readlines()

    i = 0
    wall = None
    solid_name = None
    while i < len(lines):

        line = lines[i].strip()

        if line[:len("solid")] == "solid":
            # Start new solid with one wall and multiple polygons
            solid_name = line[len("solid"):].strip()
            wall = Wall()

        elif line[:5] == "facet":
            # Start new polygon
            # Read normal from STL
            normal_coord_list = line[len("facet"):].split("normal")[1].strip().split(" ")
            normal_x = float(normal_coord_list[0])
            normal_y = float(normal_coord_list[1])
            normal_z = float(normal_coord_list[2])
            normal = np.array([normal_x, normal_y, normal_z])
            # Read vertices
            i += 1
            line = lines[i].strip()
            assert line == "outer loop"
            vertices = np.zeros((3, 3))
            for k in range(3):
                i += 1
                line = lines[i].strip()
                assert line[:len("vertex")] == "vertex"
                v = np.array([float(v) for v in line[len("vertex"):].strip().split(" ")])
                vertices[k, :] = v

            i += 1
            line = lines[i].strip()
            assert line == "endloop"

            # Add polygon
            poly = Polygon([Point(*vertices[0]), Point(*vertices[1]), Point(*vertices[2])])
            # assert np.isclose(poly.normal, normal, rtol=1e-1).all(), \
            #     f"Normal incorrect: {poly.normal} vs. {normal}"

            if wall is not None:
                wall.add_polygon(poly)
            else:
                raise ValueError("No wall created, so cannot add polygons to it.")

        elif line[:len("endsolid")] == "endsolid":
            assert line[len("endsolid"):].strip() == solid_name
            # Add solid to wall
            if wall is not None:
                if solid_name is None or solid_name == "":
                    solid_name = random_id()
                print(f"{len(wall.polygons.keys())=}")
                zone.add_solid(solid_name, [wall])
                print("Zone created")
            else:
                raise ValueError("No wall created, so cannot add it to the zone/solid.")
        else:
            pass  # Empty line?

        i += 1
        print(i)

    print("Reading STL file finished: " + path)

    return zone


if __name__ == "__main__":
    # Example
    from building3d.geom.predefined.box import box
    zone = box(2.0, 5.0, 3.0)
    write_stl("zone.stl", zone)
    zone_recovered = read_stl("zone.stl")
    write_stl("zone_recovered.stl", zone_recovered)

    example = read_stl("utah_teapot.stl")
    plot_zone(example, show_triangulation=False, show_normals=False, show=True)
