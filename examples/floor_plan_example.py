from building3d.display.plot_objects import plot_objects
from building3d.geom.solid.floor_plan import floor_plan
from building3d.geom.zone import Zone
from building3d.geom.building import Building


def run():
    building = Building(name="FloorPlanExample")

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
        plan.reverse()

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

        solid = floor_plan(
            plan=plan,
            height=height,
            translate=translate,
            rot_angle=rot_angle,
            name=name,
            wall_names=wall_names,
            floor_name=floor_name,
            ceiling_name=ceiling_name,
        )
        zone = Zone()
        zone.add_solid(solid)

        building.add_zone(zone)

    plot_objects((building,))


if __name__ == "__main__":
    run()
