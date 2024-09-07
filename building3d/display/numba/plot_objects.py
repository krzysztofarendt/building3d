import logging
from pathlib import Path

import numpy as np
import pyvista as pv

from building3d.geom.numba.types import PointType
from building3d.display.numba.colors import random_rgb_color


logger = logging.getLogger(__name__)


def plot_objects(objects: tuple, output_file=None) -> None:
    """Plot multiple objects (like Building, Zone, Solid, Wall, RayCluster).

    The faces array is organized as:
    `[n0, p0_0, p0_1, ..., p0_n, n1, p1_0, p1_1, ..., p1_n, ...]`
    where `n0` is the number of points in face 0, and `pX_Y` is the Y’th point in face X.

    The lines are organized as 2D array shaped `(num_lines, num_points_in_a_line)`.

    The object must have at least one of the following methods:
    - get_mesh() - returning points and faces -> tuple[PointType, IndexType]
    - get_lines() - returning points and lines -> tuple[PointType, IndexType]
    - get_points() - returning points -> PointType

    Args:
        objects: objects to plot, described above
        output_file: string with the path to output image, if None will show interactive plot

    Return:
        None

    Raises:
        ValueError: if len(objects) == 0
    """
    logger.info(f"Start plotting {[str(obj) for obj in objects]}")

    if len(objects) == 0:
        raise ValueError("Nothing to plot. No objects passed.")

    if output_file is None:
        pl = pv.Plotter()
    else:
        pl = pv.Plotter(off_screen=True)

    for obj in objects:

        # If more than 1 object is given, use different color for each
        if len(objects) > 1:
            col = random_rgb_color()
        else:
            col = [1.0, 1.0, 1.0]

        # Plot mesh, lines, or points, depending on which method is present
        has_get_mesh = callable(getattr(obj, "get_mesh", None))
        has_get_lines = callable(getattr(obj, "get_lines", None))
        has_get_points = callable(getattr(obj, "get_points", None))
        assert (
            has_get_mesh or has_get_lines or has_get_points
        ), f"{obj} has nothing to plot"

        if has_get_mesh:
            verts, faces = obj.get_mesh()
            faces_flat = []
            for f in faces:
                faces_flat.extend([3, f[0], f[1], f[2]])
            faces_flat = np.array(faces_flat)
            mesh = pv.PolyData(verts, faces=faces_flat)
            pl.add_mesh(mesh, show_edges=True, opacity=0.7, color=col)

        if has_get_lines:
            verts, lines = obj.get_lines()
            lines_flat = []
            for l in lines:
                segment = [len(l)]
                for v in l:
                    segment.append(int(v))
                lines_flat.extend(segment)
            mesh = pv.PolyData(verts, lines=lines_flat)
            pl.add_mesh(mesh, opacity=0.7, color=col)

        if has_get_points:
            verts = obj.get_points()
            mesh = pv.PolyData(verts)
            pl.add_mesh(mesh, opacity=0.9, point_size=5, color=col)

    if output_file is None:
        pl.show()
        logger.info(f"Image displayed")
    else:
        parent_dir = Path(output_file).parent
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True)
        pl.show(screenshot=output_file)
        logger.info(f"Image saved to {output_file}")
