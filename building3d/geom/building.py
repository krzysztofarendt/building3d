"""Building class"""
from building3d import random_id
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid


class Building:
    """Building is a collection of zones.

    Zones do not have to be adjacent. They can be even separate buildings.
    """

    def __init__(self, name: str | None = None):
        if name is None:
            name = random_id()
        self.name = name
        self.zones = {}

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
