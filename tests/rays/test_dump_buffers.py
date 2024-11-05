from tempfile import TemporaryDirectory

import numpy as np

from building3d.sim.rays.dump_buffers import dump_buffers
from building3d.sim.rays.dump_buffers import read_buffers
from building3d.geom.building import Building
from building3d.sim.rays.simulation_config import SimulationConfig


def test_dump_buffers():
    with TemporaryDirectory() as tmpdir:
        num_steps = 16
        num_rays = 8
        num_absorbers = 4

        pos_buf = np.random.random((num_steps, num_rays, 3))
        enr_buf = np.random.random((num_steps, num_rays))
        hit_buf = np.random.random((num_steps, num_absorbers))

        dummy_bdg = Building()
        sim_cfg = SimulationConfig(dummy_bdg)

        dump_buffers(pos_buf, enr_buf, hit_buf, tmpdir, sim_cfg)
        pos_buf2, enr_buf2, hit_buf2 = read_buffers(tmpdir, sim_cfg)

        assert pos_buf.shape == pos_buf2.shape
        assert enr_buf.shape == enr_buf2.shape
        assert hit_buf.shape == hit_buf2.shape

        assert np.allclose(pos_buf, pos_buf2)
        assert np.allclose(enr_buf, enr_buf2)
        assert np.allclose(hit_buf, hit_buf2)
