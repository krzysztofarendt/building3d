"""Zone class"""

from building3d.geom.solid import Solid
from building3d.geom.exceptions import GeometryError


class Zone:
    """Zone is a collection of solids with additional attributes and methods.
    """
    def __init__(self, name: str):
        self.name = name
        self.solids = {}
        self.solidgraph = {}

    def add_solid(self, sld: Solid, parent: str | None = None):
        """Add solid to the zone.

        A solid can be a top-level (parent) solid or a subsolid.
        Only 1 level of subsolids is allowed, i.e. a solid cannot be
        a subsolid to another subsolid.

        A subsolid must be entirely inside its parent solid.

        Args:
            sld: solid to be added
            parent: name of parent solid if this is a subsolid (default None)
        """
        self.solids[sld.name] = sld
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
