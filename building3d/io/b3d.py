"""B3D is the native file format for Building3D.

B3D is a JSON file that directly maps the content of the Building class.
Its structure is based on the relationships between the classes:
Building, Zone, Solid, Wall, Polygon, Point.
E.g. a zone is part of a building, a solid is part of a zone, and a wall is part of a solid.

Format:
{
    "name": Building.name,
    "zones": {
        Zone.name: {
            Solid.name: {
                Wall.name: {
                    Polygon.name: {
                        "pts": [[x0, y0, z0], ..., [xN, yN, zN]],
                        "tri": [[t0a, t0b, t0c], ..., [tMa, tMb, tMc]],
                        "uid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                    },
                    ...
                },
                ...
            },
            ...
        },
        ...
    },
}
"""

import json
from pathlib import Path

import numpy as np

from building3d.geom.building import Building
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.types import FLOAT
from building3d.geom.types import INT
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone
from building3d.types.recursive_default_dict import recursive_default_dict


def write_b3d(path: str, bdg: Building, parent_dirs: bool = True) -> None:
    """Write the model and its mesh to B3D file.

    Args:
        path: path to the output file
        bdg: Building instance
        parent_dirs: if True, parent directories will be created
    """
    if parent_dirs is True:
        p = Path(path)
        if not p.parent.exists():
            p.parent.mkdir(parents=True)

    # Construct the model dictionary
    # I am keeping only the object names and point coordinates
    bdict = recursive_default_dict()
    bdict["name"] = bdg.name

    for z in bdg.zones.values():
        for s in z.solids.values():
            for w in s.walls.values():
                for p in w.polygons.values():
                    bdict["zones"][z.name][s.name][w.name][p.name][
                        "pts"
                    ] = p.pts.tolist()
                    bdict["zones"][z.name][s.name][w.name][p.name][
                        "tri"
                    ] = p.tri.tolist()
                    bdict["zones"][z.name][s.name][w.name][p.name]["uid"] = p.uid

    # Save to JSON
    with open(path, "w") as f:
        json.dump(bdict, f, indent=None)


def read_b3d(path: str) -> Building:
    """Read the model and its mesh from B3D file."""
    with open(path, "r") as f:
        bdict = json.load(f)

    building = Building(name=bdict["name"])

    # Read geometry
    for zname in bdict["zones"]:
        zone = Zone(name=zname)
        for sname in bdict["zones"][zname]:
            walls = []
            for wname in bdict["zones"][zname][sname]:
                wall = Wall(name=wname)
                for pname in bdict["zones"][zname][sname][wname]:
                    pts = bdict["zones"][zname][sname][wname][pname]["pts"]
                    tri = bdict["zones"][zname][sname][wname][pname]["tri"]
                    uid = bdict["zones"][zname][sname][wname][pname]["uid"]
                    poly = Polygon(
                        pts=np.array(pts, dtype=FLOAT),
                        name=pname,
                        uid=uid,
                        tri=np.array(tri, dtype=INT),
                    )
                    wall.add_polygon(poly)
                walls.append(wall)
            solid = Solid(walls=walls, name=sname)
            zone.add_solid(solid)
        building.add_zone(zone)

    return building
