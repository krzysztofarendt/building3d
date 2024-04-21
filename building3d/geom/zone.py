"""Zone class"""

from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.exceptions import GeometryError


class Zone:
    """Zone is a collection of solids with additional attributes and methods.

    Solids must be adjacent.

    Zone is used to model 3D phenomena (e.g. ray tracing, heat transfer, CFD).
    """
    def __init__(self, name: str):
        self.name = name
        self.solids = {}
        self.solidgraph = {}

    def add_solid(self, name: str, walls: list[Wall]):
        """Add solid created from walls to the zone."""
        polygons = []
        for w in walls:
            polygons.extend(w.get_polygons())
        solid = Solid(name, boundary=polygons)
        self.add_solid_instance(solid)

    def add_solid_instance(self, sld: Solid, parent: str | None = None):
        """Add solid instance to the zone.

        A solid can be a top-level (parent) solid or a subsolid.
        Only 1 level of subsolids is allowed, i.e. a solid cannot be
        a subsolid to another subsolid.

        A subsolid must be entirely inside its parent solid.

        Args:
            sld: solid to be added
            parent: name of parent solid if this is a subsolid (default None)
        """
        # Check if it is adjacent to existing solids
        if len(self.solids) > 1:
            adjacent = False
            for _, existing_sld in self.solids.items():
                if sld.is_adjacent_to_solid(existing_sld):
                    adjacent = True
            if not adjacent:
                raise GeometryError(
                    f"Cannot add solid {sld.name}, because it is disconnected "
                    f"from other solids in this zone: {self.solids.keys}"
                )

        # Add solid
        self.solids[sld.name] = sld

        # Map to parent
        if parent is None:
            # This might be a parent solid
            self.solidgraph[sld.name] = []
        else:
            # Add this solid to its parent
            self.solidgraph[parent].append(sld.name)

            # Assert solid is inside parent solid
            for p in sld.vertices():
                if not self.solids[parent].is_point_inside(p):
                    raise GeometryError(
                        f"Solid {sld.name} is not entirely inside {parent} due to {p}"
                    )
