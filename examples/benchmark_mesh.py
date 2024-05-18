"""Measure mesh generation time.

This script does the following:
- generates a cube with dimensions 1x1x1m3
- generates 3d mesh in a loop with different element sizes
- measures mesh generation time
- saves results to mesh_generation_time.csv

It takes several minutes to complete (about 6 minutes on i5-11400H @ 2.70GHz).
"""
import time

import numpy as np
import pandas as pd

from building3d.geom.predefined.box import box
from building3d.mesh.mesh import Mesh


if __name__ == "__main__":
    zone = box(1.0, 1.0, 1.0)

    delta_grid = np.array([0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.125, 0.1])
    num_elements = np.zeros(len(delta_grid))
    time_res = np.zeros(len(delta_grid))

    for i, delta in enumerate(delta_grid):
        print(f"Running case {i} with {delta=}")

        mesh = Mesh(delta=delta)
        mesh.add_zone(zone)

        t0 = time.time()
        mesh.generate(solidmesh=True)
        t1 = time.time()

        num_elements[i] = len(mesh.solidmesh.elements)
        time_res[i] = t1 - t0

        print(f"num_elements = {num_elements[i]}")
        print(f"Time = {time_res[i]}")
        print()

    df = pd.DataFrame()
    df["num_elements"] = num_elements
    df["time"] = time_res
    df["delta"] = delta_grid
    df["case"] = np.arange(len(delta_grid))
    df = df.set_index("case")

    df.to_csv("mesh_generation_time.csv")
