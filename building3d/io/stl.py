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
import logging
from pathlib import Path

import numpy as np

import building3d.logger
from building3d import random_id
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone


logger = logging.getLogger(__name__)


def write_stl(path: str, zone: Zone) -> None:
    """Read STL file.

    STL does not contain information about how facets (triangles)
    are grouped together, so each facet is treated as a separate triangular wall/polygon.

    It means that if you write a zone to STL and then read it again,
    they may have different number of polygons!
    """
    logger.debug(f"Writing zone {zone.name} to STL: {path}")
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
    logger.debug(f"Number of lines in STL file = {len(lines)}")


def read_stl(path: str, verify: bool = True) -> Zone:
    """Reat zone from an STL file.

    STL does not contain information about how facets (triangles)
    are grouped together, so each facet is treated as a separate triangular wall/polygon.

    It means that if you write a zone to STL and then read it again,
    they may have different number of polygons!
    """
    logger.debug(f"Reading a zone from STL: {path}")

    zone = Zone(name=Path(path).stem, verify=verify)

    logger.debug(f"Assuming zone name based on filename: {zone.name}")

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
            if not np.isclose(poly.normal, normal, rtol=1e-2).all():
                logger.warning(f"Normal different than in STL: calculated={poly.normal} vs. stl={normal}")

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
                zone.add_solid(solid_name, [wall])
            else:
                raise ValueError("No wall created, so cannot add it to the zone/solid.")
        else:
            pass  # Empty line?

        i += 1

    logger.debug(f"Zone read from STL: {zone}")
    logger.debug(f"Number of solids in zone {zone.name} = {len(zone.solids.keys())}")

    return zone
