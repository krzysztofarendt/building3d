"""dotbim (.bim) file I/O."""
from collections import defaultdict
import json

import dotbimpy
import numpy as np

from building3d import random_id
from building3d.geom.building import Building
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.polygon import Polygon
from building3d.geom.cloud import points_to_flat_list
from building3d.geom.cloud import flat_list_to_points
from building3d.types.recursive_default_dict import recursive_default_dict


TOOL_NAME = "Building3D"


def write_dotbim(path: str, bdg: Building) -> None:
    """Save model to .bim.

    .bim format can be used to store the model geometry without the mesh.
    """
    mesh_id = 0
    meshes = []
    elements = []

    for zone in bdg.zones.values():
        for sld in zone.solids.values():
            for wall in sld.walls:
                for poly in wall.get_polygons(only_parents=False):
                    verts, faces = poly.points, poly.triangles
                    coordinates = points_to_flat_list(verts)
                    indices = np.array(faces).flatten().tolist()

                    # Instantiate Mesh object
                    mesh = dotbimpy.Mesh(
                        mesh_id=mesh_id,
                        coordinates=coordinates,
                        indices=indices,
                    )

                    # Element properties
                    color = dotbimpy.Color(r=255, g=255, b=255, a=255)
                    guid = random_id()  # NOTE: GUID not used by Building3D
                    info = {
                        "Zone": zone.name,
                        "Solid": sld.name,
                        "Wall": wall.name,
                        "Polygon": poly.name,
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
        "Building": bdg.name,
        "GeneratedBy": TOOL_NAME
    }

    # Instantiate and save File object
    file = dotbimpy.File(
        "1.0.0", meshes=meshes, elements=elements, info=file_info
    )
    file.save(path)


def read_dotbim(path: str) -> Building:
    """Load model from .bim.

    .bim format can be used to store the model geometry without the mesh.
    """
    bim = {}
    with open(path, "r") as f:
        bim = json.load(f)

    error_msg = ".bim format not compatible with Building3D"
    if not "GeneratedBy" in bim["info"].keys():
        raise KeyError(error_msg)
    elif bim["info"]["GeneratedBy"] != TOOL_NAME:
        raise ValueError(error_msg)

    # Get mesh
    data = {}
    for m in bim["meshes"]:
        mid = m["mesh_id"]
        coords = m["coordinates"]
        indices = m["indices"]
        vertices = flat_list_to_points(coords)
        faces = np.array(indices, dtype=np.int32).reshape((-1, 3)).tolist()
        data[mid] = {
            "vertices": vertices,
            "faces": faces,  # NOTE: Not used in reconstruction
        }

    # Get metadata
    bname = bim["info"]["Building"]
    for el in bim["elements"]:
        mid = el["mesh_id"]
        data[mid]["Zone"] = el["info"]["Zone"]
        data[mid]["Solid"] = el["info"]["Solid"]
        data[mid]["Wall"] = el["info"]["Wall"]
        data[mid]["Polygon"] = el["info"]["Polygon"]

    # Construct the model dictionary
    def ddict():
        """Infinite level defaultdict."""
        return defaultdict(ddict)

    model = recursive_default_dict()
    for poly_num in data.keys():
        poly_name = data[poly_num]["Polygon"]
        wall_name = data[poly_num]["Wall"]
        solid_name = data[poly_num]["Solid"]
        zone_name = data[poly_num]["Zone"]

        model[bname][zone_name][solid_name][wall_name][poly_name]["vertices"] = \
            data[poly_num]["vertices"]
        model[bname][zone_name][solid_name][wall_name][poly_name]["faces"] = \
            data[poly_num]["faces"]  # NOTE: Not used in reconstruction

    # Reconstruct the Building instance
    building = Building(name=bname)
    for zname in model[bname].keys():
        solids = []
        for sname in model[bname][zname].keys():
            walls = []
            for wname in model[bname][zname][sname].keys():
                polys = []
                for pname in model[bname][zname][sname][wname].keys():
                    polys.append(Polygon(
                        points=model[bname][zname][sname][wname][pname]["vertices"],
                        name=pname,
                    ))
                walls.append(Wall(polygons=polys, name=wname))
            solids.append(Solid(walls=walls, name=sname))
        zone = Zone(name=zname)
        for sld in solids:
            zone.add_solid_instance(sld)
        building.add_zone(zone)

    return building
