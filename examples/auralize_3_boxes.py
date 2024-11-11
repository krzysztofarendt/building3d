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
from building3d.sim.rays.dump_buffers import dump_buffers
from building3d.sim.rays.dump_buffers import read_buffers
from building3d.sim.rays.movie_from_buffer import make_movie_from_buffer
from building3d.sim.rays.ray_buff_plotter import RayBuffPlotter
from building3d.sim.rays.simulation import Simulation
from building3d.sim.rays.simulation_config import SimulationConfig
from building3d.sim.rays.impulse_response import impulse_response

if __name__ == "__main__":
    print("This example shows an auralization simulation in a building with 3 solids.")

    # Parameters
    output_dir = "out/auralize_3_boxes"
    buffer_dir = os.path.join(output_dir, "buffer")

    # Create a U-shaped building
    H = 3.0
    s0 = box(3, 8, H, (0, 0, 0), "s0")
    s1 = box(6, 3, H, (3, 5, 0), "s1")
    s2 = box(3, 5, H, (6, 0, 0), "s2")
    zone = Zone([s0, s1, s2], "z")
    building = Building([zone], "b")

    # Slice adjacent polygons to make interfaces between adjacent solids
    building.stitch_solids()

    # Plot the building to verify its geometry
    # plot_objects((building, ))

    # Simulation configuration
    sim_cfg = SimulationConfig(building)

    sim_cfg.engine["voxel_size"] = 0.3
    sim_cfg.engine["num_steps"] = 8000
    sim_cfg.rays["num_rays"] = 30000
    sim_cfg.surfaces["absorption"]["default"] = 0.05   # Smooth concrete, painted
    sim_cfg.rays["source"] = (1.0, 1.0, H / 2)
    sim_cfg.rays["absorbers"] = [
        (0.5, 0.5, H / 2),  # Close to the source
        (7.0, 0.5, H / 2),  # Far from the source
    ]

    # Simulate
    sim = Simulation(building, sim_cfg)
    t0 = time.time()
    pos_buf, enr_buf, hit_buf = sim.run()
    tot_time = time.time() - t0
    print(f"{tot_time=:.2f}")

    # Save building
    b3d_file = os.path.join(output_dir, "building.b3d")
    write_b3d(b3d_file, building)

    # Save and read buffers - if the video looks fine, these functions work OK
    dump_buffers(pos_buf, enr_buf, hit_buf, buffer_dir, sim_cfg)
    pos_buf, enr_buf, hit_buf = read_buffers(buffer_dir, sim_cfg)

    # Delete position and energy buffers to save memory
    del pos_buf
    del enr_buf

    # Save impulse response
    ir_all = impulse_response(hit_buf, sim_cfg)
    ir_all.to_csv(os.path.join(output_dir, "ir.csv"))

    # Convolve IRs and save new audio
    target_sr = int(1 / sim_cfg.engine["time_step"])
    audio, orig_sr = sf.read("resources/audio/p226_008_mic1.wav")
    audio = librosa.resample(audio, orig_sr=orig_sr, target_sr=target_sr)
    sf.write(os.path.join(output_dir, "original.wav"), data=audio, samplerate=target_sr)

    num_absorbers = len(ir_all.columns)
    for an in range(num_absorbers):
        ir = ir_all[an].to_numpy()
        t = ir_all.index.to_numpy()

        audio_ired = fftconvolve(audio, ir)
        out_path = os.path.join(output_dir, f"receiver_{an}.wav")
        sf.write(out_path, data=audio_ired, samplerate=target_sr)

    # Show plot - plotting rays takes a lot of memory!
    # rays = RayBuffPlotter(building, pos_buf, enr_buf)
    # plot_objects((building, rays))

    # Render a movie - takes a lot of time and memory!
    # make_movie_from_buffer(
    #     output_file=f"{output_dir}/movie.mp4",
    #     building=building,
    #     pos_buf=pos_buf,
    #     enr_buf=enr_buf,
    #     sim_cfg=sim_cfg,
    # )
