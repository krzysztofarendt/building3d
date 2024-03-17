import matplotlib.pyplot as plt
import numpy as np

from building3d.geom.zone import Zone
from building3d.geom.vector import length


def plot_zone(zone: Zone):
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    # Plot walls
    for wall in zone.walls:
        edges = wall.edges
        for line in edges:
            x0, y0, z0 = line[0].x, line[0].y, line[0].z
            x1, y1, z1 = line[1].x, line[1].y, line[1].z
            ax.plot([x0, x1], [y0, y1], zs=[z0, z1], color="k")

    for wall in zone.walls:
        n = wall.normal
        c = wall.centroid
        end = c + n
        x0, y0, z0 = c.x, c.y, c.z
        x1, y1, z1 = end.x, end.y, end.z

        for pt in wall.points:
            ax.text(pt.x, pt.y, pt.z, str(pt))

        assert np.isclose(length(n), 1.0)
        assert np.isclose(end.vector() - c.vector(), n).all()

        ax.plot([x0, x1], [y0, y1], zs=[z0, z1], color="red")
        ax.text(x0, y0, z0, str(c))
        ax.text(x1, y1, z1, str(end))

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_aspect("equal")

    plt.show()
