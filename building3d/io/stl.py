"""STL import/export.

This format can be used to import/export zone geometry.
There is no metadata attached, so the information
about the original structure of the model (zones, solids, walls, polygons)
is lost. Each triangle is read/written as a separate wall.
There can be multiple solids in an STL file.
One STL file = one zone.

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
"""

import logging
from pathlib import Path

import numpy as np

from building3d.random import random_id
from building3d.geom.building import Building
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.types import FLOAT
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone

logger = logging.getLogger(__name__)


def write_stl(path: str, bdg: Building, parent_dirs: bool = True) -> None:
    """Read STL file.

    STL does not contain information about how facets (triangles)
    are grouped together, so each facet is treated as a separate triangular wall/polygon.

    It means that if you write a zone to STL and then read it again,
    they may have different number of polygons!

    Args:
        path: path to the output file
        bdg: Building instance
        parent_dirs: if True, parent directories will be created
    """
    logger.debug(f"Writing building {bdg.name} ({bdg.uid}) to STL: {path}")

    if parent_dirs is True:
        p = Path(path)
        if not p.parent.exists():
            p.parent.mkdir(parents=True)

    lines = []
    l1 = " " * 2
    l2 = " " * 4
    l3 = " " * 6
    for zone in bdg.zones.values():
        for sld in zone.solids.values():
            lines.append(f"solid {sld.uid}\n")
            for wall in sld.walls.values():
                for _, poly in wall.polygons.items():
                    ni, nj, nk = poly.vn
                    for facet in poly.tri:
                        lines.append(f"{l1}facet normal {ni} {nj} {nk}\n")
                        lines.append(f"{l2}outer loop\n")
                        v1x, v1y, v1z = poly.pts[facet[0]]
                        v2x, v2y, v2z = poly.pts[facet[1]]
                        v3x, v3y, v3z = poly.pts[facet[2]]
                        lines.append(f"{l3}vertex {v1x} {v1y} {v1z}\n")
                        lines.append(f"{l3}vertex {v2x} {v2y} {v2z}\n")
                        lines.append(f"{l3}vertex {v3x} {v3y} {v3z}\n")
                        lines.append(f"{l2}endloop\n")
                        lines.append(f"{l1}endfacet\n")
            lines.append(f"endsolid {sld.uid}\n")
    with open(path, "w") as f:
        f.writelines(lines)
    logger.debug(f"Number of lines in STL file = {len(lines)}")


def read_stl(path: str) -> Building:
    """Read a building from an STL file.

    Information about zones is lost. Information about walls is lost.
    The output building has 1 zone with as many walls and polygons as
    there are triangles.

    This is because STL does not contain information about how facets (triangles)
    are grouped together.
    """
    logger.debug(f"Reading a zone from STL: {path}")

    zone = Zone()
    bdg = Building([zone], name=Path(path).stem)

    logger.debug(f"Assuming zone name based on filename: {zone.name}")

    with open(path, "r") as f:
        lines = f.readlines()

    i = 0
    wall = None
    solid_uid = None
    while i < len(lines):

        line = lines[i].strip()

        if line[: len("solid")] == "solid":
            # Start new solid with one wall and multiple polygons
            solid_uid = line[len("solid") :].strip()
            wall = Wall()

        elif line[:5] == "facet":
            # Start new polygon
            # Read normal from STL
            normal_coord_list = (
                line[len("facet") :].split("normal")[1].strip().split(" ")
            )
            normal_x = float(normal_coord_list[0])
            normal_y = float(normal_coord_list[1])
            normal_z = float(normal_coord_list[2])
            normal = np.array([normal_x, normal_y, normal_z], dtype=FLOAT)
            # Read vertices
            i += 1
            line = lines[i].strip()
            assert line == "outer loop"
            vertices = np.zeros((3, 3))
            for k in range(3):
                i += 1
                line = lines[i].strip()
                assert line[: len("vertex")] == "vertex"
                v = np.array(
                    [float(v) for v in line[len("vertex") :].strip().split(" ")],
                    dtype=FLOAT,
                )
                vertices[k, :] = v

            i += 1
            line = lines[i].strip()
            assert line == "endloop"

            # Add polygon
            poly = Polygon(vertices)
            if not np.isclose(poly.vn, normal, rtol=1e-2).all():
                logger.warning(
                    f"Normal different than in STL: calculated={poly.vn} vs. stl={normal}"
                )

            if wall is not None:
                wall.add_polygon(poly)
            else:
                raise ValueError("No wall created, so cannot add polygons to it.")

        elif line[: len("endsolid")] == "endsolid":
            assert line[len("endsolid") :].strip() == solid_uid
            # Add solid to wall
            if wall is not None:
                if solid_uid is None or solid_uid == "":
                    solid_uid = random_id()

                solid = Solid([wall])
                zone.add_solid(solid)
            else:
                raise ValueError("No wall created, so cannot add it to the zone/solid.")
        else:
            pass  # Empty line?

        i += 1

    logger.debug(f"Zone read from STL: {zone}")
    logger.debug(f"Number of solids in zone {zone.name} = {len(zone.solids.keys())}")

    return bdg
