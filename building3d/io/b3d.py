"""B3D is the native file format for Building3D.

B3D is a JSON file that directly maps the content of the Building class.
Its structure is based on the relationships between the classes:
Building, Zone, Solid, Wall, Polygon, Point.
E.g. a zone is part of a building, a solid is part of a zone, and a wall is part of a solid.

Element `uid`s are not saved. They are randomly generated when reading the file.

Format:
{
    "name": Building.name,
    "zones": {
        Zone.name: {
            Solid.name: {
                Wall.name: {
                    Polygon.name: {
                        "points": [[x0, y0, z0], ..., [xN, yN, zN]],
                        "triangles": [[t0a, t0b, t0c], ..., [tMa, tMb, tMc]],
                        "children": [Polygon.name, ...],
                        "parent": Polygon.name | None
                    },
                    ...
                },
                ...
            },
            ...
        },
        ...
    },
    "mesh": {
        "polymesh": {
            "delta": PolyMesh.delta,
            "vertices": [[x0, y0, z0], ..., [xK, yK, zK]],
            "faces": [[f0a, f0b, f0c], ..., [fFa, fFb, fFc]],
            "vertex_owners": {
                Polygon.name: [v0, ..., vK],
                ...
            },
            "face_owners": {
                Polygon.name: [f0, ..., fF],
                ...
            },
        "solidmesh": {
            "delta": SolidMesh.delta,
            "vertices": [[x0, y0, z0], ..., [xS, yS, zS]],
            "elements": [[e0a, e0b, e0c, e0d], ..., [eEa, eEb, eEc, eEd]],
            "vertex_owners": {
                Solid.name: [v0, ..., vS],
                ...
            }
            "element_owners": {
                Solid.name: [e0, ..., eE],
                ...
            },
        }
    }
}
"""
from pathlib import Path
import json

from building3d.geom.cloud import points_to_nested_list
from building3d.geom.cloud import nested_list_to_points
from building3d.geom.building import Building
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.polygon import Polygon
from building3d.geom.zone import Zone
from building3d.mesh.polymesh import PolyMesh
from building3d.mesh.solidmesh import SolidMesh
from building3d.types.recursive_default_dict import recursive_default_dict


def write_b3d(path: str, bdg: Building, parents: bool = True) -> None:
    """Write the model and its mesh to B3D file.

    Args:
        path: path to the output file
        bdg: Building instance
        parents: if True, parent directories will be created
    """
    if parents is True:
        p = Path(path)
        if not p.parent.exists():
            p.parent.mkdir(parents=True)

    # Construct the model dictionary
    # I am keeping only the object names and point coordinates
    bdict = recursive_default_dict()
    bdict["name"] = bdg.name

    # Zones (geometry)
    for zone in bdg.get_zones():
        for solid in zone.get_solids():
            for wall in solid.get_walls():
                for poly in wall.get_polygons(children=True):
                    points = points_to_nested_list(poly.points)
                    triangles = poly.triangles
                    bdict["zones"][zone.name][solid.name][wall.name][poly.name]["points"] \
                        = points
                    bdict["zones"][zone.name][solid.name][wall.name][poly.name]["triangles"] \
                        = triangles

                    children = [x.name for x in wall.get_subpolygons(poly.name)]
                    bdict["zones"][zone.name][solid.name][wall.name][poly.name]["children"] \
                        = children  # Not used when loading, but useful for debugging

                    parent = wall.get_parent_name(poly.name)
                    bdict["zones"][zone.name][solid.name][wall.name][poly.name]["parent"] \
                        = parent

    # Polygon mesh
    bdict["mesh"]["polymesh"]["delta"] = bdg.mesh.polymesh.delta
    bdict["mesh"]["polymesh"]["vertices"] = points_to_nested_list(bdg.mesh.polymesh.vertices)
    bdict["mesh"]["polymesh"]["faces"] = bdg.mesh.polymesh.faces
    bdict["mesh"]["polymesh"]["vertex_owners"] = bdg.mesh.polymesh.vertex_owners
    bdict["mesh"]["polymesh"]["face_owners"] = bdg.mesh.polymesh.face_owners

    # Solid mesh
    bdict["mesh"]["solidmesh"]["delta"] = bdg.mesh.solidmesh.delta
    bdict["mesh"]["solidmesh"]["vertices"] = points_to_nested_list(bdg.mesh.solidmesh.vertices)
    bdict["mesh"]["solidmesh"]["elements"] = bdg.mesh.solidmesh.elements
    bdict["mesh"]["solidmesh"]["vertex_owners"] = bdg.mesh.solidmesh.vertex_owners
    bdict["mesh"]["solidmesh"]["element_owners"] = bdg.mesh.solidmesh.element_owners

    # Save to JSON
    with open(path, "w") as f:
        json.dump(bdict, f, indent=1)


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

                    points = bdict["zones"][zname][sname][wname][pname]["points"]
                    triangles = bdict["zones"][zname][sname][wname][pname]["triangles"]
                    # children = bdict["zones"][zname][sname][wname][pname]["children"]  # Not used
                    parent = bdict["zones"][zname][sname][wname][pname]["parent"]

                    poly = Polygon(
                        points=nested_list_to_points(points),
                        name=pname,
                        triangles=triangles,
                    )
                    wall.add_polygon(poly, parent=parent)

                walls.append(wall)

            solid = Solid(walls=walls, name=sname)
            zone.add_solid(solid)

        building.add_zone(zone)

    # Read polygon mesh
    polymesh = PolyMesh(bdict["mesh"]["polymesh"]["delta"])
    vertices = nested_list_to_points(bdict["mesh"]["polymesh"]["vertices"])
    vertex_owners = bdict["mesh"]["polymesh"]["vertex_owners"]
    faces = bdict["mesh"]["polymesh"]["faces"]
    face_owners = bdict["mesh"]["polymesh"]["face_owners"]
    polymesh.reinit(vertices, vertex_owners, faces, face_owners)
    building.mesh.polymesh = polymesh

    # Read solid mesh
    solidmesh = SolidMesh(bdict["mesh"]["solidmesh"]["delta"])
    vertices = nested_list_to_points(bdict["mesh"]["solidmesh"]["vertices"])
    vertex_owners = bdict["mesh"]["solidmesh"]["vertex_owners"]
    elements = bdict["mesh"]["solidmesh"]["elements"]
    element_owners = bdict["mesh"]["solidmesh"]["element_owners"]
    solidmesh.reinit(vertices, vertex_owners, elements, element_owners)
    building.mesh.solidmesh = solidmesh

    return building
