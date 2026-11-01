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
from gearbox_assembly import gearbox_assembly
from shredder_components import drum_disk, fixed_knife
from pusher_mechanism import pusher_mechanism

def full_machine_assembly(config: ShredderSystemConfig):
    """
    Assembles the Gearbox, Shredder Drum, Fixed Knife, and Pusher using configuration.
    """
    motor_conf = config.motor
    gearbox_conf = config.gearbox
    shredder_conf = config.shredder

    # 1. Gearbox
    # (Includes Housing, Input Shaft, Output Hex Shaft, Impact Drive)
    gearbox = gearbox_assembly(config)

    # 2. Shredder Drum
    num_disks = shredder_conf.num_disks
    disk_thickness = shredder_conf.disk_thickness_mm
    num_teeth = shredder_conf.num_teeth_per_disk

    drum_parts = []

    # Helical pattern calculation
    angle_step = 360.0 / (num_disks * num_teeth)

    # Create one master disk to copy
    # Note: drum_disk now takes the config object
    master_disk_shape = drum_disk(config)

    # Position drum above gearbox
    # Gearbox height usually ~40-60mm housing + output shaft.
    # We need to position it where the shaft starts effectively.
    # Gearbox output shaft starts at Z=10 roughly in the sub-assembly.
    # Let's assume some clearance.

    drum_start_z = gearbox_conf.housing_height_mm + 20.0

    for i in range(num_disks):
        z_pos = drum_start_z + (i * disk_thickness)
        angle = i * angle_step

        # Copy and move
        d = master_disk_shape.rotate(Axis.Z, angle).move(Location((0,0, z_pos)))
        drum_parts.append(d)

    # 3. Fixed Knife
    # Positioned next to the drum.
    drum_diameter = shredder_conf.drum_diameter_mm
    knife_clearance = shredder_conf.fixed_knife_clearance_mm

    # Knife shape
    knife_shape = fixed_knife(config)

    # Center the knife along the drum length
    total_drum_length = num_disks * disk_thickness
    drum_center_z = drum_start_z + (total_drum_length / 2)

    # Knife X position: Radius + Clearance + (Thickness/2 ?)
    # Usually knife face is at Radius + Clearance.
    # fixed_knife returns a Box(length, width, thickness).
    # Box is centered at origin.
    # Length (from fixed_knife implementation) is the long dimension (along Drum Axis).
    # Width is usually the depth away from drum?
    # Thickness is the vertical dimension?
    # Let's check fixed_knife implementation again in my head:
    # Box(length, width, thickness).
    # Length = drum_length (Z axis effectively after rotation).
    # Width = 50.
    # Thickness = 20.

    # We rotate it 90 deg Y axis.
    # Before rotation: X=Length, Y=Width, Z=Thickness.
    # After 90 deg Y: X=Thickness, Y=Width, Z=-Length (or similar).
    # We want the "Length" to be along Z.
    # We want the "Face" (Width or Thickness) to face the drum.

    # Let's just trust visual alignment for now or precise math:
    # If we rotate 90 Y: The X axis becomes Z axis.
    # So "Length" aligns with Z.

    knife_x_pos = (drum_diameter / 2) + knife_clearance + 10 # +10 for half thickness of knife (assuming 20mm thick)
    knife_loc = Location((knife_x_pos, 0, drum_center_z))

    knife_part = knife_shape.rotate(Axis.Y, 90).move(knife_loc)

    # 4. Pusher
    # Simplified pusher placeholder
    pusher_shape = pusher_mechanism(config)

    # Position at Y negative
    pusher_loc = Location((0, -120, drum_center_z))
    pusher_part = pusher_shape.rotate(Axis.X, 90).move(pusher_loc)

    # Combine Everything
    full_assembly = Compound(children=[
        gearbox,
        *drum_parts,
        knife_part,
        pusher_part
    ])

    return full_assembly

if __name__ == "__main__":
    print("Generating Full Machine Assembly from Config...")

    # Prioritize optimized config
    optimized_path = os.path.join(os.path.dirname(__file__), 'parameters', 'optimized_shredder_config.json')
    default_path = os.path.join(os.path.dirname(__file__), 'parameters', 'shredder_config.json')

    if os.path.exists(optimized_path):
        print(f"Loading optimized config from {optimized_path}")
        cfg = ShredderSystemConfig.load_from_json(optimized_path)
    elif os.path.exists(default_path):
        print(f"Loading config from {default_path}")
        cfg = ShredderSystemConfig.load_from_json(default_path)
    else:
        print("Using default config")
        cfg = default_config

    asm = full_machine_assembly(cfg)
    export_step(asm, "open_shredder_full_assembly.step")
    print("Saved open_shredder_full_assembly.step")
