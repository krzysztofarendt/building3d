from building3d.geom.point import Point


class Ray:
    def __init__(self, init_pos: Point):
        self.pos = init_pos


class RayCluster:
    def __init__(self, rays: list[Ray]):
        self.rays = rays

    def get_mesh(self, children=False) -> tuple[list[Point], list]:
        return ([r.pos for r in self.rays], [])
