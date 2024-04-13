import logging

from mayavi import mlab

from building3d.mesh.exceptions import MeshError
from building3d.mesh.solidmesh import SolidMesh
import building3d.display.colors as colors


logger = logging.getLogger(__name__)


def plot_solidmesh(
    mesh: SolidMesh,
    show: bool = False,
    opacity: int = 1.0,
):
    logger.debug(f"Starting plot_solidmesh() for {mesh}")
    # Plot tetrahedral wireframe
    # Vertices: a, b, c, d
    # Edges:
    # 1. a -> b
    # 2. b -> c
    # 3. c -> a
    # 4. a -> d
    # 5. d -> b
    # 6. c -> d
    if len(mesh.solids) <= 0:
        raise MeshError("plot_mesh(..., interior=True, ...) but SolidMesh empty")

    tri = []
    x = [p.x for p in mesh.vertices]
    y = [p.y for p in mesh.vertices]
    z = [p.z for p in mesh.vertices]
    for el in mesh.elements:
        tri.append([el[0], el[1], el[2]])
        tri.append([el[0], el[1], el[3]])
        tri.append([el[1], el[2], el[3]])
        tri.append([el[0], el[2], el[3]])

    _ = mlab.triangular_mesh(
        x, y, z, tri,
        opacity=opacity,
        line_width=1.0,
        color=colors.RGB_WHITE,
        representation="mesh",
    )

    logger.debug(f"Finished plot_solidmesh() for {mesh}")

    if show:
        mlab.show()
        return
    else:
        return

