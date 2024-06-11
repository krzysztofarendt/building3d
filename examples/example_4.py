import building3d.logger
from building3d.display.plot_building import plot_building
from building3d.display.plot_mesh import plot_mesh
from building3d.geom.building import Building
from building3d.geom.predefined.floor_plan import floor_plan
from building3d.io.b3d import write_b3d
from building3d.io.dotbim import write_dotbim
from building3d.mesh.quality.mesh_stats import mesh_stats


if __name__ == "__main__":

    building = Building(name="Example4")

    for floor_num in range(6):
        width = 25
        depth = 7
        wing_width = 7
        wing_depth = 7

        plan = [
            (0, 0),  # 1
            (width, 0),  # 2
            (width, depth + wing_depth),  # 3
            (width - wing_width, depth + wing_depth),  # 4
            (width - wing_width, depth),  # 5
            (wing_width, depth),  # 6
            (wing_width, depth + wing_depth),  # 7
            (0, depth + wing_depth),  # 8
        ]

        height = 3
        translate = (0, 0, floor_num * height)
        rot_angle = 0.0

        name = f"level_{floor_num}"
        wall_names = [
            f"wall-S-{floor_num}",
            f"wall-E-{floor_num}",
            f"wall-N-right-wing-{floor_num}",
            f"wall-patio-right-{floor_num}",
            f"wall-patio-center-{floor_num}",
            f"wall-patio-left-{floor_num}",
            f"wall-N-left-wing-{floor_num}",
            f"wall-W-{floor_num}",
        ]
        floor_name = f"floor_{floor_num}"
        ceiling_name = f"ceiling_{floor_num}"
        apertures = {
            "window-S-{floor_num}a": (f"wall-S-{floor_num}", 0.2, 0.2, 0.1, 0.6),
            "window-S-{floor_num}b": (f"wall-S-{floor_num}", 0.4, 0.2, 0.1, 0.6),
            "window-S-{floor_num}c": (f"wall-S-{floor_num}", 0.6, 0.2, 0.1, 0.6),
            "window-S-{floor_num}d": (f"wall-S-{floor_num}", 0.8, 0.2, 0.1, 0.6),
            "window-E-{floor_num}a": (f"wall-E-{floor_num}", 1 / 4, 0.3, 0.1, 0.6),
            "window-E-{floor_num}b": (f"wall-E-{floor_num}", 1 / 2, 0.3, 0.1, 0.6),
            "window-E-{floor_num}c": (f"wall-E-{floor_num}", 3 / 4, 0.3, 0.1, 0.6),
            "window-N-right-wing-{floor_num}a": (f"wall-N-right-wing-{floor_num}", 0.5, 0.3, 0.5, 0.6),
            "window-patio-center-{floor_num}a": (f"wall-patio-center-{floor_num}", 0.5, 0.3, 0.5, 0.6),
            "window-N-left-wing-{floor_num}a": (f"wall-N-left-wing-{floor_num}", 0.5, 0.3, 0.5, 0.6),
            "window-W-{floor_num}a": (f"wall-W-{floor_num}", 1 / 4, 0.3, 0.1, 0.6),
            "window-W-{floor_num}b": (f"wall-W-{floor_num}", 1 / 2, 0.3, 0.1, 0.6),
            "window-W-{floor_num}c": (f"wall-W-{floor_num}", 3 / 4, 0.3, 0.1, 0.6),
        }

        zone = floor_plan(
            plan = plan,
            height = height,
            translate = translate,
            rot_angle = rot_angle,
            name = name,
            wall_names = wall_names,
            floor_name = floor_name,
            ceiling_name = ceiling_name,
            apertures = apertures,
        )

        building.add_zone(zone)

    plot_building(building)
    write_b3d("example_4.b3d", building)
    write_dotbim("example_4.bim", building)
