"""Zone class"""

from .solid import Solid


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
