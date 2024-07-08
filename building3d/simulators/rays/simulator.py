from building3d.geom.building import Building
from building3d import random_between
from building3d.geom.point import Point
from building3d.simulators.basesimulator import BaseSimulator
from building3d.simulators.rays.ray import Ray
from building3d.simulators.rays.cluster import RayCluster


class RaySimulator(BaseSimulator):

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

    def forward(self):
        self.r_cluster.forward()

    def is_finished(self):
        return False
