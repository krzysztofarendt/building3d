"""dotbim (.bim) file I/O."""

from collections import defaultdict
import json
from pathlib import Path

import dotbimpy
import numpy as np

from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.polygon import Polygon
from building3d.geom.types import FLOAT, INT
from building3d.types.recursive_default_dict import recursive_default_dict


TOOL_NAME = "Building3D"


def write_dotbim(path: str, bdg: Building, parent_dirs: bool = True) -> None:
    """Save model to .bim.

    Args:
        path: path to the output file
        bdg: Building instance
        parent_dirs: if True, parent directories will be created
    """
    if parent_dirs is True:
        p = Path(path)
        if not p.parent.exists():
            p.parent.mkdir(parents=True)

    mesh_id = 0
    meshes = []
    elements = []

    for zone in bdg.zones.values():
        for sld in zone.solids.values():
            for wall in sld.walls.values():
                for poly in wall.polygons.values():
                    coordinates = poly.pts.flatten().tolist()
                    indices = poly.tri.flatten().tolist()

                    # Instantiate Mesh object
                    mesh = dotbimpy.Mesh(
                        mesh_id=mesh_id,
                        coordinates=coordinates,
                        indices=indices,
                    )

                    # Element properties
                    color = dotbimpy.Color(r=255, g=255, b=255, a=255)
                    guid = poly.uid
                    info = {
                        "zone_name": zone.name,
                        "zone_uid": zone.uid,
                        "solid_name": sld.name,
                        "solid_uid": sld.uid,
                        "wall_name": wall.name,
                        "wall_uid": wall.uid,
                        "polygon_name": poly.name,
                        "polygon_uid": poly.uid,
                    }
                    rotation = dotbimpy.Rotation(qx=0, qy=0, qz=0, qw=1.0)
                    type = poly.name
                    vector = dotbimpy.Vector(x=0, y=0, z=0)

                    # Instantiate Element object
                    element = dotbimpy.Element(
                        mesh_id=mesh_id,
                        vector=vector,
                        guid=guid,
                        info=info,
                        rotation=rotation,
                        type=type,
                        color=color,
                    )

                    # Add to lists
                    meshes.append(mesh)
                    elements.append(element)

                    mesh_id += 1

    # File meta data
    file_info = {
        "building_name": bdg.name,
        "building_uid": bdg.uid,
        "generated_by": TOOL_NAME,
    }

    # Instantiate and save File object
    file = dotbimpy.File("1.0.0", meshes=meshes, elements=elements, info=file_info)
    file.save(path)


def read_dotbim(path: str) -> Building:
    """Load model from .bim."""
    bim = {}
    with open(path, "r") as f:
        bim = json.load(f)

    error_msg = ".bim format not compatible with Building3D"
    if not "generated_by" in bim["info"].keys():
        raise KeyError(error_msg)
    elif bim["info"]["generated_by"] != TOOL_NAME:
        raise ValueError(error_msg)

    # Get mesh
    data = {}
    for m in bim["meshes"]:
        mid = m["mesh_id"]
        coords = m["coordinates"]
        indices = m["indices"]
        vertices = np.array(coords, dtype=FLOAT).reshape((-1, 3))
        faces = np.array(indices, dtype=INT).reshape((-1, 3))
        data[mid] = {
            "vertices": vertices,
            "faces": faces,
        }

    # Get metadata
    bname = bim["info"]["building_name"]
    buid = bim["info"]["building_uid"]
    for el in bim["elements"]:
        mid = el["mesh_id"]
        data[mid]["zone_name"] = el["info"]["zone_name"]
        data[mid]["zone_uid"] = el["info"]["zone_uid"]
        data[mid]["solid_name"] = el["info"]["solid_name"]
        data[mid]["solid_uid"] = el["info"]["solid_uid"]
        data[mid]["wall_name"] = el["info"]["wall_name"]
        data[mid]["wall_uid"] = el["info"]["wall_uid"]
        data[mid]["polygon_name"] = el["info"]["polygon_name"]
        data[mid]["polygon_uid"] = el["info"]["polygon_uid"]

    # Construct the model dictionary
    def ddict():
        """Infinite level defaultdict."""
        return defaultdict(ddict)

    model = recursive_default_dict()
    for poly_num in data.keys():
        poly_name = data[poly_num]["polygon_name"]
        poly_uid = data[poly_num]["polygon_uid"]
        wall_name = data[poly_num]["wall_name"]
        wall_uid = data[poly_num]["wall_uid"]
        solid_name = data[poly_num]["solid_name"]
        solid_uid = data[poly_num]["solid_uid"]
        zone_name = data[poly_num]["zone_name"]
        zone_uid = data[poly_num]["zone_uid"]

        zkey = (zone_uid, zone_name)
        skey = (solid_uid, solid_name)
        wkey = (wall_uid, wall_name)
        pkey = (poly_uid, poly_name)

        model[bname][zkey][skey][wkey][pkey]["vertices"] = data[poly_num]["vertices"]
        model[bname][zkey][skey][wkey][pkey]["faces"] = data[poly_num]["faces"]

    # Reconstruct the Building instance
    building = Building(name=bname, uid=buid)
    for zkey in model[bname].keys():
        zuid, zname = zkey
        solids = []
        for skey in model[bname][zkey].keys():
            suid, sname = skey
            walls = []
            for wkey in model[bname][zkey][skey].keys():
                wuid, wname = wkey
                polys = []
                for pkey in model[bname][zkey][skey][wkey].keys():
                    puid, pname = pkey
                    polys.append(
                        Polygon(
                            pts=model[bname][zkey][skey][wkey][pkey]["vertices"],
                            name=pname,
                            tri=model[bname][zkey][skey][wkey][pkey]["faces"],
                            uid=puid,
                        )
                    )
                walls.append(Wall(polygons=polys, name=wname, uid=wuid))
            solids.append(Solid(walls=walls, name=sname, uid=suid))
        zone = Zone(name=zname, uid=zuid)
        for sld in solids:
            zone.add_solid(sld)
        building.add_zone(zone)

    return building
