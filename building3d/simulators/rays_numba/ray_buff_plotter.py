import numpy as np

from building3d.display.plot_objects import plot_objects
from building3d.geom.building import Building
from building3d.geom.types import PointType, FLOAT, FloatDataType


class RayBuffPlotter:
    """Class with methods for plotting the rays as points and lines based on the ray buffer."""

    def __init__(self, building: Building, pos_buf: PointType, enr_buf: FloatDataType):
        self.building = building
        self.pos_buf = pos_buf
        self.enr_buf = enr_buf

    def plot(self):
        building_color = (1.0, 1.0, 1.0)
        ray_color = (1.0, 0.0, 0.0)
        colors = [building_color, ray_color]
        plot_objects((self.building, self), colors=colors)

    def get_points(self):
        return self.pos_buf[-1, :, :]

    def get_lines(self):
        line_len = self.pos_buf.shape[0]
        num_rays = self.pos_buf.shape[1]
        verts = []
        lines = []
        curr_index = 0
        for rn in range(num_rays):
            verts.extend(self.pos_buf[:, rn, :])
            lines.append([curr_index + i for i in range(line_len)])
            curr_index += line_len

        return np.vstack(verts, dtype=FLOAT), np.vstack(lines)
