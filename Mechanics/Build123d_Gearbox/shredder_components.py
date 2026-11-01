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

# =============================================================================
# 1. Carbide Insert Model
# =============================================================================
def carbide_insert_ccmt060204():
    """
    Generates a CCMT060204 Carbide Insert.
    Dimensions derived from standard or the provided SCAD file.
    """
    # Parameters for CCMT 06 02 04
    # l = 6.4mm (Cutting edge length)
    # s = 2.38mm (Thickness)
    # r = 0.4mm (Corner radius)
    # d1 = 2.8mm (Hole diameter) ? SCAD says 2.5/3-48
    # 80 degree diamond shape

    thickness = 2.38

    # Create the Diamond Profile
    # Side length ~ 6.35mm
    # Angle 80 deg.

    side_len = 6.35
    angle = 80

    with BuildPart() as insert:
        with BuildSketch() as profile:
            # Create a Rhombus/Diamond
            # Using RegularPolygon doesn't give 80deg easily.
            # Let's draw a trapezoid/rhombus manually.

            # 80 deg rhombus.
            # Side = 6.35.
            # D_long = 2 * 6.35 * cos(40) = 9.72
            # D_short = 2 * 6.35 * sin(40) = 8.16

            # Pts: (D_long/2, 0), (0, D_short/2), (-D_long/2, 0), (0, -D_short/2)
            pts = [
                (4.86, 0),
                (0, 4.08),
                (-4.86, 0),
                (0, -4.08)
            ]
            with BuildLine() as l:
                Polyline(pts, close=True)
            make_face()
            fillet(profile.vertices(), radius=0.4)

        # Extrude with Relief Angle (7 deg)
        # Taper Extrude?
        # C implies 7 deg relief.
        # Positive insert: bottom is smaller than top.
        # So we extrude Tapered?
        # extrude(taper=7) ?
        extrude(amount=thickness, taper=7)

        # Screw Hole (Countersunk)
        with Locations((0,0, thickness)): # Top face
            CounterSinkHole(radius=2.8/2, counter_sink_radius=4.5/2, depth=thickness)

    return insert.part

# =============================================================================
# 2. Shredder Drum Disk
# =============================================================================
def drum_disk(config: ShredderSystemConfig):
    """
    Generates a single slice of the shredder drum using configuration.
    """
    shredder_conf = config.shredder

    diameter = shredder_conf.drum_diameter_mm
    thickness = shredder_conf.disk_thickness_mm
    hex_shaft_size = shredder_conf.hex_bore_mm
    num_teeth = shredder_conf.num_teeth_per_disk

    with BuildPart() as disk:
        Cylinder(radius=diameter/2, height=thickness)

        # Hex Bore
        # Hexagon with flat-to-flat = hex_shaft_size
        # Radius (Center to Corner) = size / sqrt(3) * 2 ?
        # Flat-to-Flat (s) = 2 * r_inscribed
        # r_inscribed = s/2 = 12.5
        # r_circumscribed (Radius for RegularPolygon) = r_inscribed / cos(30) = (s/2) / (sqrt(3)/2) = s / sqrt(3)
        # 25 / 1.732 = 14.43

        hex_radius = hex_shaft_size / math.sqrt(3)
        with Locations((0,0)):
            with BuildSketch():
                RegularPolygon(radius=hex_radius, side_count=6)
            extrude(amount=thickness, mode=Mode.SUBTRACT)

        # Tooth Pockets
        # We cut out a recess for the Insert + backing.
        # For a shredder, we usually have a "Tooth" protruding, or the drum is the tooth?
        # Standard design: The disk IS the cutter. It has "Hooks".
        # The carbide insert is mounted on the leading face of the hook.

        # Let's model a "Hook" profile.
        # We start with a Cylinder, but we carve out "Gullets" to form teeth.

        # Hook depth
        tooth_depth = 20.0

        insert = carbide_insert_ccmt060204()

        for i in range(num_teeth):
            angle = i * (360.0 / num_teeth)

            # 1. Cut the Gullet (The space in front of the tooth)
            # A simple cylinder cut or box cut
            with Locations(Rotation(0,0, angle)):
                with Locations((diameter/2, 15, 0)): # Offset position
                    Cylinder(radius=25, height=thickness, mode=Mode.SUBTRACT)

            # 2. Mount the Insert
            # On the "Face" created by the gullet.
            # Position is approximate for this demo.
            with Locations(Rotation(0,0, angle)):
                 with Locations((diameter/2 - 5, -5, thickness/2)): # Position on the hook tip
                     with Locations(Rotation(90, -90, 0)): # Orient correctly (facing forward)
                         # We subtract the insert shape (pocket)
                         add(insert, mode=Mode.SUBTRACT)

                         # Add screw hole clearance if needed (simplified)

    return disk.part

# =============================================================================
# 3. Fixed Knife (Counter Blade)
# =============================================================================
def fixed_knife(config: ShredderSystemConfig):
    """
    A simple rectangular bar with a profile matching the drum?
    Usually it's a comb shape.
    For this demo, we'll make a simple bar.
    """
    shredder_conf = config.shredder

    length = shredder_conf.drum_length_mm
    drum_diameter = shredder_conf.drum_diameter_mm
    width = 50.0 # Could be parameterized
    thickness = 20.0 # Could be parameterized

    with BuildPart() as knife:
        Box(length, width, thickness)

        # If we had the full drum profile, we would cut "Teeth" into this knife
        # to interleave with the drum spacers.
        # Assuming the drum has spacers between disks?
        # Or if the disks are packed tight, the knife is just a straight bar
        # (simpler, but less efficient shearing).
        # Let's assume a straight bar for the MVP.

    return knife.part

if __name__ == "__main__":
    print("Generating Shredder Components from Config...")

    # Load config or use default
    config_path = os.path.join(os.path.dirname(__file__), 'parameters', 'shredder_config.json')
    if os.path.exists(config_path):
        print(f"Loading config from {config_path}")
        cfg = ShredderSystemConfig.load_from_json(config_path)
    else:
        print("Using default config")
        cfg = default_config

    # 1. Insert (Standard part, no config needed usually)
    ins = carbide_insert_ccmt060204()
    export_step(ins, "carbide_insert.step")

    # 2. Drum Disk
    disk = drum_disk(cfg)
    export_step(disk, "shredder_drum_disk.step")

    # 3. Fixed Knife
    knife = fixed_knife(cfg)
    export_step(knife, "fixed_knife.step")

    print("Saved components.")
