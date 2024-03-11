import matplotlib.pyplot as plt

from building3d.geom.space import Space


def plot_space(space: Space):
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    # Plot walls
    for wall in space.walls:
        edges = wall.edges
        for line in edges:
            x0, y0, z0 = line[0].x, line[0].y, line[0].z
            x1, y1, z1 = line[1].x, line[1].y, line[1].z
            ax.plot([x0, x1], [y0, y1], zs=[z0, z1], color="k")

    # Plot normal vectors
    for wall in space.walls:
        normal = wall.normal
        x0, y0, z0 = normal[0].x, normal[0].y, normal[0].z
        x1, y1, z1 = normal[1].x, normal[1].y, normal[1].z
        ax.plot([x0, x1], [y0, y1], zs=[z0, z1], color="red")

    plt.show()
