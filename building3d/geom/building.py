"""Building class"""
from __future__ import annotations

import numpy as np

from building3d import random_id
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.point import Point
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.polygon import Polygon
import building3d.mesh.mesh as mesh
from building3d.config import MESH_DELTA


class Building:
    """Building is a collection of zones.

    Zones do not have to be adjacent. They can even be separate buildings.
    """
    def __init__(self, name: str | None = None, uid: str | None = None):
        """Initialize the building.

        Args:
            name: name of the building
            uid: unique id of the building, random if None
        """
        if name is None:
            name = random_id()
        self.name = validate_name(name)
        if uid is not None:
            self.uid = uid
        else:
            self.uid = random_id()
        self.zones: dict[str, Zone] = {}  # {Zone.name: Zone}
        self.mesh = mesh.Mesh()

    def add_zone(self, zone: Zone) -> None:
        """Add a Zone instance."""
        self.zones[zone.name] = zone

    def get_zone_names(self) -> list[str]:
        """Get list of zone names."""
        return list(self.zones.keys())

    def get_zones(self) -> list[Zone]:
        """Get list of zones."""
        return list(self.zones.values())

    def get_object(self, path: str) -> Zone | Solid | Wall | Polygon | None:
        """Get object by the path. The path contains names of nested components."""
        names = path.split("/")
        zone_name = names.pop(0)

        if zone_name not in self.get_zone_names():
            raise ValueError(f"Zone {zone_name} not found")
        elif len(names) == 0:
            return self.zones[zone_name]
        else:
            return self.zones[zone_name].get_object("/".join(names))

    def volume(self) -> float:
        """Calculate building volume as the sum of zone volumes."""
        volume = 0.0
        for z in self.zones.values():
            volume += z.volume()
        return volume

    def get_mesh(
        self,
        children: bool = True,
    ) -> tuple[list[Point], list[tuple[int, ...]]]:
        """Get vertices and faces of this building's polygons.

        This function returns faces generated by the ear-clipping algorithm.

        Args:
            children: if True, will include subpolygons

        Return:
            tuple of vertices and faces
        """
        verts = []
        faces = []

        for z in self.zones.values():
            offset = len(verts)
            v, f = z.get_mesh(children)
            verts.extend(v)
            f = np.array(f) + offset
            f = [tuple(x) for x in f]
            faces.extend(f)

        return verts, faces

    def generate_simulation_mesh(
        self,
        delta: float | None = None,
        include_volumes: bool = False,
    ) -> None:
        """Generate mesh suitable for numerical simulations.

        Generates surface mesh by default (`PolyMesh`).
        If `include_volumes` is `True`, generates also the volume mesh (`SolidMesh`).

        Args:
            delta: approximate element size, will use default is `None`
            include_volumes: if True, will generate surface and volume meshes
        """
        if delta is None:
            delta = MESH_DELTA

        self.mesh = mesh.Mesh(delta=delta)

        for zone in self.get_zones():
            self.mesh.add_zone(zone)

        self.mesh.generate(solidmesh=include_volumes)

    def __eq__(self, other) -> bool:
        """Returns True if all zones of this and other are equal."""
        if len(self.zones.values()) != len(other.zones.values()):
            return False
        else:
            num_matches = 0
            for this_zone in self.zones.values():
                for other_zone in other.zones.values():
                    if this_zone == other_zone:
                        num_matches += 1
                        break
            if num_matches != len(self.zones.values()):
                return False
            return True
