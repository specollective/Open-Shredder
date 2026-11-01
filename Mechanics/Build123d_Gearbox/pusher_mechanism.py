import sys
import os

try:
    from parameters.shredder_config import ShredderSystemConfig, default_config
except ImportError:
    # Add parameters directory to sys.path if running as script
    sys.path.append(os.path.join(os.path.dirname(__file__), 'parameters'))
    from shredder_config import ShredderSystemConfig, default_config

from build123d import *

def pusher_mechanism(config: ShredderSystemConfig):
    """
    Generates the Pusher Plate based on configuration.
    """
    shredder_conf = config.shredder

    # Pusher width should fit inside the hopper which is slightly larger than drum length
    # Let's make it match drum length for now or slightly less.
    width = shredder_conf.drum_length_mm - 4.0 # 2mm clearance each side
    depth = shredder_conf.drum_diameter_mm - 10.0 # Slightly smaller than drum diameter
    thickness = 20.0 # Could be in config

    # 1. Pusher Plate
    # A heavy block that pushes plastic down.
    with BuildPart() as pusher:
        Box(width, depth, thickness)

        # Add Handle / Actuator mount on top
        with Locations((0,0, thickness/2)):
            Box(50, 50, 20, mode=Mode.ADD)

    return pusher.part

if __name__ == "__main__":
    print("Generating Pusher from Config...")
    config_path = os.path.join(os.path.dirname(__file__), 'parameters', 'shredder_config.json')
    if os.path.exists(config_path):
        print(f"Loading config from {config_path}")
        cfg = ShredderSystemConfig.load_from_json(config_path)
    else:
        print("Using default config")
        cfg = default_config

    pusher = pusher_mechanism(cfg)
    export_step(pusher, "pusher_plate.step")
    print("Saved pusher_plate.step")
