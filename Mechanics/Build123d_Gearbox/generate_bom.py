import sys
import os
import csv
from dataclasses import dataclass, field
from typing import List

try:
    from parameters.shredder_config import ShredderSystemConfig, default_config
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'parameters'))
    from shredder_config import ShredderSystemConfig, default_config

@dataclass
class BOMItem:
    category: str  # "Printed", "Hardware", "Electronics"
    name: str
    quantity: int
    material: str = "N/A"
    notes: str = ""
    unit_mass_g: float = 0.0 # Estimated mass for printed parts

class BOMGenerator:
    def __init__(self, config: ShredderSystemConfig):
        self.config = config
        self.items: List[BOMItem] = []

    def generate(self):
        """Calculates the BOM based on configuration."""
        motor = self.config.motor
        gearbox = self.config.gearbox
        shredder = self.config.shredder
        mat = self.config.material

        # 1. Electronics
        self.items.append(BOMItem("Electronics", f"Motor: {motor.type}", 1, "N/A", f"{motor.torque_nm}Nm Torque"))
        self.items.append(BOMItem("Electronics", "Motor Driver", 1, "TB6600 or DM556", "Suitable for NEMA34"))
        self.items.append(BOMItem("Electronics", "Power Supply", 1, "48V DC", "Min 350W"))
        self.items.append(BOMItem("Electronics", "Arduino Controller", 1, "Nano/Uno", "Motion Control"))

        # 2. Hardware (Fasteners & Bearings)
        # Bearings
        # Output Shaft Bearings (x2)
        bearing_id = gearbox.output_shaft_hex_mm # Actually, usually cylindrical journal on hex shaft?
        # Or standard bearing on hex adapter?
        # Let's assume standard bearings fitting the Hex OD (Flat-Flat?) No, usually corner-to-corner.
        # Let's just list "Bearings for Output Shaft"
        self.items.append(BOMItem("Hardware", f"Bearing for {gearbox.output_shaft_hex_mm}mm Hex", 2, "Steel", "ID matches Shaft Hex Corners"))

        # Input Shaft Bearings (x2)
        self.items.append(BOMItem("Hardware", f"Bearing ID {motor.shaft_diameter_mm}mm", 2, "Steel", "Input Shaft Support"))

        # Bolts for Motor Mount
        self.items.append(BOMItem("Hardware", "Motor Mount Bolts", 4, "M5/M6", f"Length > {gearbox.housing_height_mm}mm"))

        # Bolts for Housing Assembly
        self.items.append(BOMItem("Hardware", "Housing Assembly Bolts", 4, "M5", "Length 50mm"))

        # Inserts for Drum
        total_inserts = shredder.num_disks * shredder.num_teeth_per_disk
        self.items.append(BOMItem("Hardware", "Carbide Insert CCMT060204", total_inserts, "Carbide", "Cutting Edges"))
        self.items.append(BOMItem("Hardware", "Insert Screw M2.5", total_inserts, "Steel", "Torx Head"))

        # 3. Printed Parts (Estimates)
        density = 1.25 # g/cm3 for PLA/PETG approx (1250 kg/m3)

        # Gearbox Housing
        # Cylinder volume - Cavity
        h_vol = (3.14159 * (motor.housing_od_mm/2)**2 * gearbox.housing_height_mm) - \
                (3.14159 * (75.0/2)**2 * (gearbox.housing_height_mm-5))
        # Convert mm3 to cm3: / 1000
        h_mass = (h_vol / 1000.0) * density * 0.4 # 40% Infill approx
        self.items.append(BOMItem("Printed", "Gearbox Housing", 1, "PETG/Nylon", "", h_mass))

        # Cycloidal Disk
        # Area * Thickness
        d_vol = (3.14159 * (gearbox.pin_circle_diameter_mm/2)**2 * 5.0) # Approx
        d_mass = (d_vol / 1000.0) * density * 1.0 # 100% Infill for gears
        self.items.append(BOMItem("Printed", "Cycloidal Disk", 1, "Nylon/PC", "High Strength", d_mass))

        # Shredder Disks
        # Annulus Area * Thickness
        # OD = drum_dia, ID = hex_bore
        # ID Area approx hex area ~ 0.866 * hex^2
        id_area = 0.866 * shredder.hex_bore_mm**2
        od_area = 3.14159 * (shredder.drum_diameter_mm/2)**2
        disk_vol = (od_area - id_area) * shredder.disk_thickness_mm
        total_disk_mass = (disk_vol / 1000.0) * density * 1.0 # 100% Infill

        self.items.append(BOMItem("Printed", "Shredder Drum Disk", shredder.num_disks, "PLA/PETG", "Consumable?", total_disk_mass))

        # Pusher
        p_vol = (shredder.drum_length_mm * (shredder.drum_diameter_mm-10) * 20.0)
        p_mass = (p_vol / 1000.0) * density * 0.2 # 20% Infill
        self.items.append(BOMItem("Printed", "Pusher Plate", 1, "PLA", "", p_mass))

    def write_csv(self, filepath):
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Item Name", "Quantity", "Material", "Notes", "Est. Unit Mass (g)"])

            for item in self.items:
                writer.writerow([
                    item.category,
                    item.name,
                    item.quantity,
                    item.material,
                    item.notes,
                    f"{item.unit_mass_g:.1f}" if item.unit_mass_g > 0 else "-"
                ])

if __name__ == "__main__":
    print("Generating Bill of Materials...")

    # Load optimized or default
    optimized_path = os.path.join(os.path.dirname(__file__), 'parameters', 'optimized_shredder_config.json')
    default_path = os.path.join(os.path.dirname(__file__), 'parameters', 'shredder_config.json')

    if os.path.exists(optimized_path):
        print(f"Using optimized config: {optimized_path}")
        cfg = ShredderSystemConfig.load_from_json(optimized_path)
    elif os.path.exists(default_path):
        print(f"Using default config: {default_path}")
        cfg = ShredderSystemConfig.load_from_json(default_path)
    else:
        cfg = default_config

    bom = BOMGenerator(cfg)
    bom.generate()

    output_path = "BOM.csv"
    bom.write_csv(output_path)
    print(f"BOM saved to {output_path}")
