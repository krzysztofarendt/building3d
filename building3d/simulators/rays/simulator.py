from building3d.types.recursive_default_dict import recursive_default_dict
from building3d.geom.building import Building
from building3d import random_between
from building3d.geom.point import Point
from building3d.simulators.basesimulator import BaseSimulator
from building3d.simulators.rays.ray import Ray
from building3d.simulators.rays.cluster import RayCluster
from building3d.geom.paths import PATH_SEP


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
        time_step: float = 1e-3,
    ):
        self.building = building
        self.source = source
        self.receiver = receiver
        self.receiver_radius = receiver_radius
        self.speed = speed
        self.time_step = time_step

        self.r_cluster = RayCluster(speed=speed, time_step=time_step)
        self.r_cluster.add_rays(source=source, num_rays=num_rays)

        self.transparent_polys = self.find_transparent_polygons(building)

        # TODO: Decide if subpolygons are of any use here
        # TODO: Add specular reflections
        ...

    def forward(self):
        # Find solid for each point
        self.r_cluster.forward()

    def find_transparent_polygons(self, building: Building) -> list[str]:
        """Find and return the list of transparent polygons in the building.

        A polygon is transparent if it separates two adjacent solids within a single zone.
        """
        graph = building.get_graph()
        print(graph)

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
