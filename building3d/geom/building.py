"""Building class"""
from __future__ import annotations

from building3d import random_id
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid
from building3d.mesh.mesh import Mesh
from building3d.config import MESH_DELTA


class Building:
    """Building is a collection of zones.

    Zones do not have to be adjacent. They can be even separate buildings.
    """

    def __init__(self, name: str | None = None):
        if name is None:
            name = random_id()
        self.name = name
        self.zones = {}
        self.mesh = Mesh()

    def add_zone(self, name: str, solids: list[Solid]) -> None:
        """Add zone created from solids."""
        zone = Zone(name=name)
        for sld in solids:
            zone.add_solid_instance(sld)
        self.add_zone_instance(zone)

    def add_zone_instance(self, zone: Zone) -> None:
        """Add a Zone instance."""
        self.zones[zone.name] = zone

    def volume(self) -> float:
        """Calculate building volume as the sum of zone volumes."""
        volume = 0.0
        for z in self.zones.values():
            volume += z.volume()
        return volume

    def generate_mesh(self, delta: float | None = None, include_volumes: bool = False) -> None:
        """Generate mesh suitable for numerical simulations.

        Generates surface mesh by default (`PolyMesh`).
        If `include_volumes` is `True`, generates also the volume mesh (`SolidMesh`).

        Args:
            delta: approximate element size, will use default is `None`
            include_volumes: if True, will generate surface and volume meshes
        """
        if delta is None:
            delta = MESH_DELTA

        self.mesh = Mesh(delta=delta)

        for zone in self.zones.values():
            self.mesh.add_zone(zone)

        self.mesh.generate(solidmesh=include_volumes)
