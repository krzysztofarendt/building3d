from tqdm import tqdm

from building3d.types.recursive_default_dict import recursive_default_dict
from building3d.geom.building import Building
from building3d.geom.polygon import Polygon
from building3d import random_between
from building3d.geom.point import Point
from building3d.simulators.basesimulator import BaseSimulator
from building3d.simulators.rays.ray import Ray
from building3d.simulators.rays.cluster import RayCluster
from building3d.geom.paths import PATH_SEP
from building3d.geom.paths.object_path import object_path
from building3d.geom.paths.object_path import split_path


class RaySimulator(BaseSimulator):
    """Simulator class for ray tracing.

    Controls:
    - time steps
    - source and receiver
    - reflections
    - absorption
    - when to finish
    """
    def __init__(
        self,
        building: Building,
        source: Point,
        receiver: Point,
        receiver_radius: float,
        num_rays: int = 1000,
        speed: float = 343.0,
        time_step: float = 1e-4,
    ):
        self.building = building
        self.source = source
        self.receiver = receiver
        self.receiver_radius = receiver_radius
        self.speed = speed
        self.time_step = time_step
        self.min_distance = speed * time_step * 1.01

        self.r_cluster = RayCluster(speed=speed, time_step=time_step)
        self.r_cluster.add_rays(source=source, num_rays=num_rays)

        self.transparent_polys = self.find_transparent_polygons(building)
        print(self.transparent_polys)

        # Find the location of the rays inside the building (zone_name/solid_name)
        self.location = None
        path_to_solid = ""
        for z in building.get_zones():
            for s in z.get_solids():
                if s.is_point_inside(source):
                    path_to_solid = object_path(zone=z, solid=s)
                    self.location = [path_to_solid for _ in range(self.r_cluster.size)]

        if self.location is None:
            raise RuntimeError("Ray source outside solid.")

        # Find the next blocking surface (polygon)
        # Directions of rays are already known, so we can look at all polygons in the current solid
        # This will enable to track only one polygon per ray until the ray hits the surface
        zname, sname = split_path(path_to_solid)
        z = building.zones[zname]
        s = z.solids[sname]

        self.next_surface = []
        self.dist = []
        print("Finding next blocking surface for each ray...")  # TODO: Add logger
        for r in tqdm(self.r_cluster.rays):
            found = False
            for w in s.get_walls():
                for p in w.get_polygons():
                    if p.is_point_inside_projection(r.position, r.velocity):
                        self.next_surface.append(object_path(zone=z, solid=s, wall=w, poly=p))
                        self.dist.append(p.distance_point_to_polygon(r.position))
                        found = True
                        break
                if found:
                    break
            if not found:
                # This should not happen, because all rays are initilized inside a solid
                # and solids must be fully enclosed with polygons
                raise RuntimeError("Some ray is not going towards any surface... (?)")

        print(self.next_surface)
        print(self.dist)
        # TODO:
        # - Decide if properties (transparency, absorption, scattering)
        #   should be stored here or in Wall
        # - Decide if subpolygons are of any use here
        # - Add specular reflections
        ...

    def forward(self):
        # If distance below threshold, reflect (change direction)
        for i in range(self.r_cluster.size):
            if self.dist[i] < self.min_distance:
                # TODO: Reflect if not transparent
                ...
                print(f"Reflect {i}")

        # For those that were reflected or moved through transparent surf., update next surface
        ...  # TODO

        # Move rays forward
        self.r_cluster.forward()

        # Update distance to next surface
        for i in range(self.r_cluster.size):
            poly = self.building.get_object(self.next_surface[i])
            assert isinstance(poly, Polygon)
            self.dist[i] = poly.distance_point_to_polygon(self.r_cluster.rays[i].position)

        print(self.dist)

    def find_transparent_polygons(self, building: Building) -> list[str]:
        """Find and return the list of transparent polygons in the building.

        A polygon is transparent if it separates two adjacent solids within a single zone.
        """
        graph = building.get_graph()

        transparent_polys = []
        added = set()

        for k, v in graph.items():
            if k not in added or v not in added:
                z0, _, _, _ = k.split(PATH_SEP)
                if v is not None:
                    z1, _, _, _ = v.split(PATH_SEP)
                    # Doesn't have to check if p0 is facing p1,
                    # because if they are in the graph, they must be
                    if z0 == z1:
                        transparent_polys.extend([k, v])
                        added.add(k)
                        added.add(v)

        return transparent_polys

    def is_finished(self):
        return False
