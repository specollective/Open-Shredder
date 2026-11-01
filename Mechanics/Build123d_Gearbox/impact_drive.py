from build123d import *

def impact_drive_mechanism(
    shaft_diameter=8.0,
    disk_diameter=60.0,
    thickness=10.0,
    hammer_length=40.0,
    hammer_width=15.0
):
    """
    Generates the Slip Disk and Impact Hammer components.

    Concept:
    - Slip Disk: Attached to the input shaft via friction (clutch). It has a catch/dog.
    - Impact Hammer: A weighted arm that rotates freely for a bit, then strikes the catch.

    For 3D printing, we might use a simplified version:
    - The "Slip Disk" is just a flywheel with a notch.
    - The "Hammer" is an arm with a matching protrusion.
    """

    # 1. Slip Disk (Input Side)
    # A cylinder with a cutout (dog) for the hammer to hit
    with BuildPart() as slip_disk_part:
        Cylinder(radius=disk_diameter/2, height=thickness)

        # Central hole for shaft (tight fit or keyed)
        with Locations((0,0)):
            Cylinder(radius=shaft_diameter/2, height=thickness, mode=Mode.SUBTRACT)

        # The "Dog" / Catch
        # We cut a sector out or add a block. Let's add a driving block.
        # Mode.ADD is the correct enum for addition in newer build123d? Or maybe default is ADD.
        # Checking docs or common usage: Mode.ADD usually.
        with Locations((disk_diameter/2 - 5, 0, 0)): # Centered in Z? Box default center is true
             # If center=True (default), then z-location 0 is fine if we want it centered on the cylinder center?
             # Cylinder is centered at (0,0,0) by default? No, Cylinder is centered at current location.
             # Let's align it properly.
            Box(10, 10, thickness, mode=Mode.ADD)

    # 2. Impact Hammer (Output Side / Floating)
    # An arm that fits over the shaft (loose fit) and has a corresponding block
    with BuildPart() as hammer_part:
        with Locations((0,0)):
             Cylinder(radius=shaft_diameter/2 + 5.0, height=thickness) # Hub (Loose)

        # Arm
        with Locations((hammer_length/2, 0)):
             Box(hammer_length, hammer_width, thickness, mode=Mode.ADD)

        # Center Hole
        with Locations((0,0)):
             Cylinder(radius=shaft_diameter/2 + 0.2, height=thickness, mode=Mode.SUBTRACT)

        # Impact Face (The Anvil)
        # Positioned to intersect with the Slip Disk's dog after ~300 degrees of rotation
        # For now, just a block on the end
        with Locations((hammer_length - 5, 0, 0)):
             Box(10, 15, thickness, mode=Mode.ADD)

    return slip_disk_part.part, hammer_part.part

if __name__ == "__main__":
    print("Generating Impact Mechanism...")
    slip, hammer = impact_drive_mechanism()
    export_step(slip, "slip_disk.step")
    export_step(hammer, "impact_hammer.step")
    print("Saved slip_disk.step and impact_hammer.step")
