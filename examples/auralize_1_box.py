"""
It is the medium room from this analysis:
https://reuk.github.io/wayverb/evaluation.html

The Sabine's reverberation time formula states that:
T60 = 0.161 * V / A

where:
- V is the room volume (m3)
- A is the total absorption, calculated as below

A = sum(Si * ai)

where Si is the surface area of each material
and ai is the absorption coefficient of that material.

For this room T60 is as follows:
V = 39.375
a = 0.1
S = 71.5
T60 = 0.161 * 39.375 / (71.5 * 0.1) = 0.89 s
"""
import os
import time

from scipy.signal import fftconvolve
import soundfile as sf
import librosa

from building3d.display.plot_objects import plot_objects
from building3d.geom.building import Building
from building3d.geom.solid.box import box
from building3d.geom.zone import Zone
from building3d.io.b3d import write_b3d
from building3d.sim.rays.dump_buffers import read_buffers
from building3d.sim.rays.simulation import Simulation
from building3d.sim.rays.simulation_config import SimulationConfig
from building3d.sim.rays.impulse_response import impulse_response

if __name__ == "__main__":
    print("This example shows an auralization simulation in a building with 1 solid.")

    # Create a U-shaped building
    W = 4.5
    L = 2.5
    H = 3.5
    s = box(W, L, H, (0, 0, 0), "s")
    zone = Zone([s], "z")
    building = Building([zone], "b")

    # Slice adjacent polygons to make interfaces between adjacent solids
    building.stitch_solids()

    # Plot the building to verify its geometry
    plot_objects((building, ))

    # Simulation configuration
    sim_cfg = SimulationConfig(building)

    sim_cfg.paths["project_dir"] = os.path.join("out", "auralize_1_box")
    sim_cfg.paths["buffer_dir"] = os.path.join(sim_cfg.paths["project_dir"], "states")
    sim_cfg.engine["voxel_size"] = 0.1
    sim_cfg.engine["num_steps"] = 3500
    sim_cfg.rays["num_rays"] = 3000
    sim_cfg.surfaces["absorption"]["default"] = 0.1   # Smooth concrete, painted
    sim_cfg.rays["source"] = (W / 2 - 1, L / 2, H / 2)
    sim_cfg.rays["absorbers"] = [(W / 2 + 1, L / 2, H / 2)]

    # Simulate
    sim = Simulation(building, sim_cfg)
    t0 = time.time()
    pos_buf, enr_buf, hit_buf = sim.run()
    tot_time = time.time() - t0
    print(f"{tot_time=:.2f}")

    # Save building
    b3d_file = os.path.join(sim_cfg.paths["project_dir"], "building.b3d")
    write_b3d(b3d_file, building)

    # Read all buffer files
    pos_buf, enr_buf, hit_buf = read_buffers(sim_cfg.paths["buffer_dir"], sim_cfg)

    # Save impulse response
    ir_all = impulse_response(hit_buf, sim_cfg)
    ir_all.to_csv(os.path.join(sim_cfg.paths["project_dir"], "ir.csv"))

    # Convolve IRs and save new audio
    target_sr = int(1 / sim_cfg.engine["time_step"])
    audio, orig_sr = sf.read("resources/audio/p226_008_mic1.wav")
    audio = librosa.resample(audio, orig_sr=orig_sr, target_sr=target_sr)
    sf.write(os.path.join(sim_cfg.paths["project_dir"], "original.wav"), data=audio, samplerate=target_sr)

    num_absorbers = len(ir_all.columns)
    for an in range(num_absorbers):
        ir = ir_all[an].to_numpy()
        t = ir_all.index.to_numpy()

        audio_ired = fftconvolve(audio, ir)
        out_path = os.path.join(sim_cfg.paths["project_dir"], f"receiver_{an}.wav")
        sf.write(out_path, data=audio_ired, samplerate=target_sr)
