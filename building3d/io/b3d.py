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
                        "points": [[x0, y0, z0], ..., [xN, yN, zN]],
                        "triangles": [[t0a, t0b, t0c], ..., [tMa, tMb, tMc]],
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
            "vertices": [[x0, y0, z0], ..., [xK, yK, zK]],
            "faces": [[f0a, f0b, f0c], ..., [fFa, fFb, fFc]],
            "vertex_owners": {
                Polygon.name: [v0, ..., vK],
                ...
            },
        "solidmesh": {
            "vertices": [[x0, y0, z0], ..., [xS, yS, zS]],
            "elements": [[e0a, e0b, e0c, e0d], ..., [eEa, eEb, eEc, eEd]],
            "vertex_owners": {
                Solid.name: [v0, ..., vS],
                ...
            }
        }
    }
}
"""
import json

from building3d.geom.cloud import points_to_nested_list
from building3d.geom.cloud import nested_list_to_points
from building3d.geom.building import Building
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.polygon import Polygon
from building3d.geom.zone import Zone
from building3d.types.recursive_default_dict import recursive_default_dict


def write_b3d(path: str, bdg: Building) -> None:
    """Write the model and its mesh to B3D file."""

    # Construct the model dictionary
    # I am keeping only the object names and point coordinates
    bdict = recursive_default_dict()
    bdict["name"] = bdg.name

    # Zones (geometry)
    for zone in bdg.zones.values():
        for solid in zone.solids.values():
            for wall in solid.walls:  # TODO: walls should be a dict, to keep consistency
                for poly in wall.polygons.values():
                    points = points_to_nested_list(poly.points)
                    triangles = poly.triangles
                    bdict["zones"][zone.name][solid.name][wall.name][poly.name]["points"] \
                        = points
                    bdict["zones"][zone.name][solid.name][wall.name][poly.name]["triangles"] \
                        = triangles

    # Polygon mesh
    bdict["mesh"]["polymesh"]["vertices"] = points_to_nested_list(bdg.mesh.polymesh.vertices)
    bdict["mesh"]["polymesh"]["faces"] = bdg.mesh.polymesh.faces
    bdict["mesh"]["polymesh"]["vertex_owners"] = bdg.mesh.polymesh.vertex_owners
    bdict["mesh"]["polymesh"]["face_owners"] = bdg.mesh.polymesh.face_owners

    # Solid mesh
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

    for zname in bdict["zones"]:
        zone = Zone(name=zname)

        for sname in bdict["zones"][zname]:

            walls = []
            for wname in bdict["zones"][zname][sname]:

                polygons = []
                for pname in bdict["zones"][zname][sname][wname]:

                    points = bdict["zones"][zname][sname][wname][pname]["points"]
                    triangles = bdict["zones"][zname][sname][wname][pname]["triangles"]

                    poly = Polygon(
                        points=nested_list_to_points(points),
                        name=pname,
                        triangles=triangles,
                    )

                    polygons.append(poly)

                wall = Wall(polygons=polygons, name=wname)
                walls.append(wall)

            solid = Solid(walls=walls, name=sname)
            zone.add_solid_instance(solid)  # TODO: Parent solids not implemented yet

        building.add_zone_instance(zone)

    return building
