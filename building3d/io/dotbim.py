"""dotbim (.bim) file I/O."""
import dotbimpy
import numpy as np

from building3d.geom.building import Building
from building3d.geom.cloud import points_to_flat_list


def write_dotbim(path: str, bdg: Building) -> None:
    mesh_id = 0
    meshes = []
    elements = []

    for zone in bdg.zones.values():
        for sld in zone.solids.values():
            for wall in sld.walls:
                for poly in wall.get_polygons(only_parents=True):  # TODO: False
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
                    guid = poly.name
                    info = {
                        "Wall": wall.name,
                        "Solid": sld.name,
                        "Zone": zone.name,
                    }
                    rotation = dotbimpy.Rotation(qx=0, qy=0, qz=0, qw=1.0)
                    type = "Polygon"
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
    }

    # Instantiate and save File object
    file = dotbimpy.File(
        "1.0.0", meshes=meshes, elements=elements, info=file_info
    )
    file.save(path)
