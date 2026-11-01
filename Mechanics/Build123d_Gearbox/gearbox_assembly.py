import math
import sys
import os

try:
    from parameters.shredder_config import ShredderSystemConfig, default_config
except ImportError:
    # Add parameters directory to sys.path if running as script
    sys.path.append(os.path.join(os.path.dirname(__file__), 'parameters'))
    from shredder_config import ShredderSystemConfig, default_config

from build123d import *
from cycloidal_gear import cycloidal_disk
from impact_drive import impact_drive_mechanism

def gearbox_assembly(config: ShredderSystemConfig):
    """
    Generates the full gearbox assembly based on the provided configuration.
    """

    # Extract config sections for convenience
    motor_conf = config.motor
    gearbox_conf = config.gearbox
    bearing_conf = config.bearing

    # 1. Generate Cycloidal Components
    disk = cycloidal_disk(
        pin_circle_diameter=gearbox_conf.pin_circle_diameter_mm,
        num_lobes=gearbox_conf.num_lobes,
        num_pins=gearbox_conf.num_pins
    )

    # 2. Configure Motor Interface
    housing_od = motor_conf.housing_od_mm
    mount_spacing = motor_conf.mount_spacing_mm
    input_shaft_dia = motor_conf.shaft_diameter_mm
    inner_cavity_dia = 75.0 # Could be parameterized in gearbox_conf if needed

    # Determine mount style based on motor type string or add to config?
    # For now, keep the logic based on type string for backward compat/simplicity
    if motor_conf.type == "WIPER":
        mount_style = "POLAR"
        mount_count = 3
    else: # NEMA34, NEMA23, GRID
        mount_style = "GRID"
        mount_count = 4

    # 3. Housing
    housing_height = gearbox_conf.housing_height_mm

    with BuildPart() as housing:
        Cylinder(radius=housing_od/2, height=housing_height)
        with Locations((0,0)):
            Cylinder(radius=inner_cavity_dia/2, height=housing_height-5, mode=Mode.SUBTRACT) # Inner cavity

        # Motor Mount Holes
        hole_radius = 6.5 / 2 if motor_conf.type in ["NEMA34", "WIPER"] else 5.5 / 2
        with Locations((0,0, -housing_height/2)):
            if mount_style == "GRID":
                with GridLocations(mount_spacing, mount_spacing, 2, 2):
                    Cylinder(radius=hole_radius, height=10, mode=Mode.SUBTRACT)
            elif mount_style == "POLAR":
                with PolarLocations(radius=mount_spacing/2, count=mount_count):
                    Cylinder(radius=hole_radius, height=10, mode=Mode.SUBTRACT)

        # Bearing Pocket (Top Face)
        # Positioned at the top face (Z = +housing_height/2)
        pocket_center_z = housing_height/2 - bearing_conf.width_mm/2
        with Locations((0,0, pocket_center_z)):
             Cylinder(radius=bearing_conf.outer_diameter_mm/2, height=bearing_conf.width_mm, mode=Mode.SUBTRACT)

    # 4. Shafts
    output_shaft_hex = gearbox_conf.output_shaft_hex_mm

    with BuildPart() as input_shaft:
        Cylinder(radius=input_shaft_dia/2, height=gearbox_conf.input_shaft_length_mm)

    with BuildPart() as output_shaft:
        # Hex Shaft
        circum_radius = output_shaft_hex / math.sqrt(3)
        with BuildSketch():
            RegularPolygon(radius=circum_radius, side_count=6)
        extrude(amount=gearbox_conf.output_shaft_length_mm)

        # Bearing Journal
        # Aligned with the bearing pocket when shaft is at (0,0,0)
        # Pocket Z center relative to housing center is `pocket_center_z`
        with Locations((0,0, pocket_center_z)):
             Cylinder(radius=bearing_conf.inner_diameter_mm/2, height=bearing_conf.width_mm)

    # 5. Assembly List
    # Visualization Bearing
    # Using Cylinder with hole (Tube)
    # Tube(od, id, height)
    with BuildPart() as bearing_vis:
         Cylinder(radius=bearing_conf.outer_diameter_mm/2, height=bearing_conf.width_mm)
         Cylinder(radius=bearing_conf.inner_diameter_mm/2, height=bearing_conf.width_mm, mode=Mode.SUBTRACT)

    parts_list = [
        housing.part,
        disk.move(Location((0,0,5))), # Shift disk up
        input_shaft.part.move(Location((0,0,-10))),
        output_shaft.part, # Located at (0,0,0) to align with housing
        bearing_vis.part.move(Location((0,0, pocket_center_z)))
    ]

    # 6. Impact Drive (Optional)
    if gearbox_conf.use_impact_drive:
        slip, hammer = impact_drive_mechanism(shaft_diameter=input_shaft_dia)
        # Attach Slip Disk to Input Shaft (top)
        parts_list.append(slip.move(Location((0,0, 40))))
        parts_list.append(hammer.move(Location((0,0, 55))))

    assembly = Compound(children=parts_list)
    return assembly

if __name__ == "__main__":
    print("Generating Gearbox Assembly from Config...")
    # Load config or use default
    config_path = os.path.join(os.path.dirname(__file__), 'parameters', 'shredder_config.json')
    if os.path.exists(config_path):
        print(f"Loading config from {config_path}")
        cfg = ShredderSystemConfig.load_from_json(config_path)
    else:
        print("Using default config")
        cfg = default_config

    asm = gearbox_assembly(cfg)
    export_step(asm, "shredder_gearbox_assembly.step")
    print("Saved shredder_gearbox_assembly.step")
