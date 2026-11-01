import sys
import os
import math

try:
    from parameters.shredder_config import ShredderSystemConfig, default_config
except ImportError:
    # Add parameters directory to sys.path if running as script
    sys.path.append(os.path.join(os.path.dirname(__file__), 'parameters'))
    from shredder_config import ShredderSystemConfig, default_config

class DesignValidator:
    def __init__(self, config: ShredderSystemConfig):
        self.config = config
        self.errors = []
        self.warnings = []

    def check_geometry(self):
        """Checks for geometric conflicts."""
        motor = self.config.motor
        gearbox = self.config.gearbox
        shredder = self.config.shredder

        # 1. Shaft Fit
        if gearbox.output_shaft_hex_mm != shredder.hex_bore_mm:
            self.errors.append(
                f"Mismatch: Gearbox output hex ({gearbox.output_shaft_hex_mm}mm) != "
                f"Shredder bore ({shredder.hex_bore_mm}mm)."
            )

        # 2. Shaft Length
        # Drum stack length = num_disks * thickness
        drum_stack_length = shredder.num_disks * shredder.disk_thickness_mm
        required_shaft_length = drum_stack_length + 20.0 # Clearances/Threads
        if gearbox.output_shaft_length_mm < required_shaft_length:
            self.errors.append(
                f"Shaft too short: Gearbox shaft {gearbox.output_shaft_length_mm}mm < "
                f"Required {required_shaft_length}mm (Drum Stack)."
            )

        # 3. Drum Diameter vs Gearbox Housing
        # If the drum is directly above the gearbox, ensure the drum teeth clear the housing?
        # Gearbox Housing OD = 120mm usually.
        # Drum Diameter = 150mm.
        # Radius: 60mm vs 75mm. Clearance = 15mm.
        clearance = (shredder.drum_diameter_mm - motor.housing_od_mm) / 2
        if clearance < 5.0:
            self.warnings.append(
                f"Low clearance between Drum ({shredder.drum_diameter_mm}mm) and "
                f"Motor Housing ({motor.housing_od_mm}mm). Clearance: {clearance}mm."
            )

    def check_mechanics(self):
        """Checks for mechanical feasibility."""
        motor = self.config.motor
        gearbox = self.config.gearbox
        shredder = self.config.shredder
        material = self.config.material

        # 1. Torque Output
        # Efficiency of Cycloidal Drive ~ 70-85%
        efficiency = 0.8
        output_torque = motor.torque_nm * gearbox.ratio * efficiency

        # 2. Required Torque Calculation (Simplified)
        # Force = Shear Strength * Area
        # Area = Material Thickness * Cut Length (Simultaneous teeth engaging)

        # Assumption: Shredding PET Plastic (Yield ~ 50-80 MPa, Shear ~ 0.6 * Yield)
        plastic_shear_strength = 40.0 * 1e6 # 40 MPa

        # Assume we shred a bottle wall thickness of 1mm
        plastic_thickness = 1.0e-3 # 1mm

        # Cut Width = Width of one tooth or chunk size?
        # Assume we are shearing a strip equal to disk thickness?
        # No, "Nibbling". The cut width is usually small.
        # Let's assume we engage `num_teeth_per_disk` simultaneous cuts?
        # Actually, helical arrangement means usually 1 or 2 teeth engage at once.
        simultaneous_cuts = 2
        cut_width = 10.0e-3 # 10mm chunk width

        shear_area = plastic_thickness * cut_width * simultaneous_cuts
        shear_force = plastic_shear_strength * shear_area # Newtons

        # Torque = Force * Radius
        # Radius = Drum Radius (Tip)
        drum_radius = (shredder.drum_diameter_mm / 2) / 1000.0 # meters
        required_torque = shear_force * drum_radius

        if output_torque < required_torque:
            self.errors.append(
                f"Insufficient Torque: Output {output_torque:.2f} Nm < Required {required_torque:.2f} Nm "
                f"(for shearing 1mm PET)."
            )
        else:
            safety_factor = output_torque / required_torque
            if safety_factor < 1.5:
                self.warnings.append(
                    f"Low Torque Safety Factor: {safety_factor:.2f} (Goal > 1.5)."
                )

        # 3. Output Speed
        output_rpm = motor.max_rpm / gearbox.ratio
        if output_rpm > 100:
            self.warnings.append(f"Output Speed High: {output_rpm:.1f} RPM. Recommended < 60 RPM for safety/torque.")
        if output_rpm < 10:
            self.warnings.append(f"Output Speed Low: {output_rpm:.1f} RPM. Throughput may be low.")

    def run(self):
        self.check_geometry()
        self.check_mechanics()
        return len(self.errors) == 0

def validate_config(config: ShredderSystemConfig, verbose=True):
    validator = DesignValidator(config)
    valid = validator.run()

    if verbose:
        print("\n--- Design Validation Report ---")
        if validator.errors:
            print("ERRORS:")
            for e in validator.errors:
                print(f"  [X] {e}")
        else:
            print("Errors: None")

        if validator.warnings:
            print("WARNINGS:")
            for w in validator.warnings:
                print(f"  [!] {w}")
        else:
            print("Warnings: None")

        print(f"Result: {'PASS' if valid else 'FAIL'}")
        print("--------------------------------\n")

    return valid, validator.errors, validator.warnings

if __name__ == "__main__":
    # Load optimized or default
    optimized_path = os.path.join(os.path.dirname(__file__), 'parameters', 'optimized_shredder_config.json')
    default_path = os.path.join(os.path.dirname(__file__), 'parameters', 'shredder_config.json')

    if os.path.exists(optimized_path):
        print(f"Loading optimized config from {optimized_path}")
        cfg = ShredderSystemConfig.load_from_json(optimized_path)
    elif os.path.exists(default_path):
        print(f"Loading config from {default_path}")
        cfg = ShredderSystemConfig.load_from_json(default_path)
    else:
        cfg = default_config

    validate_config(cfg)
