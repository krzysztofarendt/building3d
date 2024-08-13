import logging

import numpy as np

from building3d import random_id
from building3d.geom.paths.validate_name import validate_name
from building3d.geom.paths.object_path import object_path
from building3d.geom.numba.points import new_point
from building3d.geom.numba.types import PointType, IndexType
from building3d.geom.numba.solid import Solid
from building3d.geom.numba.wall import Wall
from building3d.geom.numba.polygon import Polygon
from building3d.geom.exceptions import GeometryError


logger = logging.getLogger(__name__)


class Zone:
    """Zone is a collection of solids with additional attributes and methods.

    Solids must be adjacent. (TODO: I think, this is not checked at the moment)

    Zone is used to model 3D phenomena (e.g. ray tracing, heat transfer, CFD).
    """
    def __init__(self, name: str | None = None, uid: str | None = None):
        """Initialize the zone.

        Args:
            name: name of the zone
            uid: unique id of the zone, random if None
        """
        if name is None:
            name = random_id()
        self.name = validate_name(name)
        if uid is not None:
            self.uid = uid
        else:
            self.uid = random_id()
        self.solids: dict[str, Solid] = {}  # {Solid.name: Solid}

        logger.info(f"Zone created: {self}")

    def add_solid(self, sld: Solid) -> None:
        """Add a Solid instance to the zone.

        Args:
            sld: solid to be added
        """
        # Check if it is adjacent to existing solids
        if len(self.solids) > 1:
            adjacent = False
            for _, existing_sld in self.solids.items():
                if sld.is_adjacent_to_solid(existing_sld, exact=False):
                    adjacent = True
            if not adjacent:
                raise GeometryError(
                    f"Cannot add solid {sld.name}, because it is disconnected "
                    f"from other solids in this zone: {self.solids.keys}"
                )

        # Add solid
        self.solids[sld.name] = sld

        logger.info(f"Solid {sld.name} added: {self}")

    def get_solid_names(self) -> list[str]:
        """Get list of solid names."""
        return list(self.solids.keys())

    def get_solids(self) -> list[Solid]:
        """Get list of solids."""
        return list(self.solids.values())

    def get_wall_names(self) -> list[str]:
        """Get list of wall names."""
        return [name for sld in self.get_solids() for name in sld.get_wall_names()]

    def get_walls(self) -> list[Wall]:
        """Get list of wall instances."""
        return [w for sld in self.get_solids() for w in sld.get_walls()]

    def find_wall(self, wall_name: str) -> str:
        """Find wall by name. Return path suitable for get_object(). Will search in all solids."""
        for sld in self.get_solids():
            for wall in sld.get_walls():
                if wall.name == wall_name:
                    return object_path(solid=sld, wall=wall)
        raise GeometryError(f"Wall {wall_name} not found")

    def get_object(self, path: str) -> Solid | Wall | Polygon | None:
        """Get object by the path. The path contains names of nested components."""
        names = path.split("/")
        solid_name = names.pop(0)

        if solid_name not in self.get_solid_names():
            raise ValueError(f"Solid not found: {solid_name}")
        elif len(names) == 0:
            return self.solids[solid_name]
        else:
            return self.solids[solid_name].get_object("/".join(names))

    def get_mesh(
        self,
        children: bool = True,
    ) -> tuple[PointType, IndexType]:
        """Get vertices and faces of all solids. Used mostly for plotting.

        This function returns faces generated by the ear-clipping algorithm.

        Args:
            children: if True, parent and subpolygons are returned

        Return:
            tuple of vertices and faces
        """
        verts = []
        faces = []
        for sld in self.solids.values():
            offset = len(verts)
            v, f = sld.get_mesh(children)
            verts.extend(v.tolist())
            f += offset
            faces.extend(f.tolist())

        verts_arr = np.vstack(verts)
        faces_arr = np.array(faces)

        return verts_arr, faces_arr

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

    def __str__(self):
        s = f"Zone(name={self.name}, "
        s += f"solids={self.get_solid_names()}, "
        s += f"volume={self.volume():.2f}, "
        s += f"id={hex(id(self))})"
        return s

