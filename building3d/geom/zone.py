"""Zone class"""
import numpy as np

from building3d import random_id
from building3d.geom.point import Point
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.exceptions import GeometryError


class Zone:
    """Zone is a collection of solids with additional attributes and methods.

    Solids must be adjacent.

    Zone is used to model 3D phenomena (e.g. ray tracing, heat transfer, CFD).
    """
    def __init__(self, name: str | None = None, verify: bool = True):
        if name is None:
            name = random_id()
        self.name = name
        self.solids = {}
        self.solidgraph = {}  # TODO: Is this used and needed?
        self.verify = verify

    def add_solid(self, name: str, walls: list[Wall]) -> None:
        """Add solid created from walls to the zone."""
        solid = Solid(walls=walls, name=name, verify=self.verify)
        self.add_solid_instance(solid)

    def add_solid_instance(self, sld: Solid, parent: str | None = None) -> None:
        """Add a Solid instance to the zone.

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

    def get_mesh(
        self,
        only_parents: bool = True,
    ) -> tuple[list[Point], list[tuple[int, ...]]]:
        """Get vertices and faces of all solids. Used mostly for plotting.

        This function returns faces generated by the ear-clipping algorithm.
        """
        verts = []
        faces = []
        for sld in self.solids.values():
            offset = len(verts)
            v, f = sld.get_mesh(only_parents)
            verts.extend(v)
            f = np.array(f) + offset
            f = [tuple(x) for x in f]
            faces.extend(f)

        return verts, faces

    def volume(self) -> float:
        """Calculate zone volume as the sum of solid volumes."""
        volume = 0.0
        for sld in self.solids.values():
            volume += sld.volume
        return volume

    def __eq__(self, other) -> bool:
        """Returns True if all solids of this and other are equal."""
        if len(self.solids.values()) != len(other.solids.values()):
            return False
        else:
            num_matches = 0
            for this_solid in self.solids.values():
                for other_solid in other.solids.values():
                    if this_solid == other_solid:
                        num_matches += 1
                        break
            if num_matches != len(self.solids.values()):
                return False
        return True
