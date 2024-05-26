from dotbimpy import File

from building3d.geom.building import Building
from building3d.geom.predefined.box import box
from building3d.io.dotbim import write_dotbim


if __name__ == "__main__":
    zone_1 = box(1, 1, 1, (0, 0, 0), name="Zone_1")
    zone_2 = box(1, 1, 1, (1, 0, 0), name="Zone_2")
    zones = [zone_1, zone_2]
    building = Building(name="building")
    for z in zones:
        building.add_zone_instance(z)

    write_dotbim("building.bim", building)

    # TODO: Add read_dotbim()
    file = File.read("building.bim")
    print(file)
