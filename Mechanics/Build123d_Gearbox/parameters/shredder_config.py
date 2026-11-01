from dataclasses import dataclass, field
import json
import math

@dataclass
class MotorConfig:
    type: str = "NEMA34"
    torque_nm: float = 4.5  # Typical NEMA 34 holding torque
    shaft_diameter_mm: float = 14.0
    housing_od_mm: float = 120.0
    mount_spacing_mm: float = 69.6
    max_rpm: float = 600.0  # Conservative stepper limit

@dataclass
class GearboxConfig:
    ratio: float = 10.0
    num_lobes: int = 10
    num_pins: int = 11
    pin_circle_diameter_mm: float = 50.0
    housing_height_mm: float = 40.0
    input_shaft_length_mm: float = 60.0
    output_shaft_hex_mm: float = 25.0
    output_shaft_length_mm: float = 150.0 # Increased to clear drum
    use_impact_drive: bool = True

@dataclass
class ShredderConfig:
    drum_diameter_mm: float = 150.0
    drum_length_mm: float = 254.0
    num_disks: int = 10
    disk_thickness_mm: float = 25.4
    hex_bore_mm: float = 25.0 # Must match gearbox output hex
    num_teeth_per_disk: int = 2
    fixed_knife_clearance_mm: float = 1.0 # Gap between knife and teeth

@dataclass
class MaterialProperties:
    shaft_yield_strength_mpa: float = 250.0  # Mild Steel
    housing_yield_strength_mpa: float = 30.0 # PETG/PLA
    density_kg_m3: float = 7850.0 # Steel

@dataclass
class BearingConfig:
    series: str = "6006"
    inner_diameter_mm: float = 30.0
    outer_diameter_mm: float = 55.0
    width_mm: float = 13.0

@dataclass
class ShredderSystemConfig:
    motor: MotorConfig = field(default_factory=MotorConfig)
    gearbox: GearboxConfig = field(default_factory=GearboxConfig)
    shredder: ShredderConfig = field(default_factory=ShredderConfig)
    material: MaterialProperties = field(default_factory=MaterialProperties)
    bearing: BearingConfig = field(default_factory=BearingConfig)

    def save_to_json(self, filepath: str):
        data = {
            "motor": self.motor.__dict__,
            "gearbox": self.gearbox.__dict__,
            "shredder": self.shredder.__dict__,
            "material": self.material.__dict__,
            "bearing": self.bearing.__dict__
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load_from_json(cls, filepath: str):
        with open(filepath, 'r') as f:
            data = json.load(f)

        config = cls()
        # Update nested configs
        if "motor" in data: config.motor = MotorConfig(**data["motor"])
        if "gearbox" in data: config.gearbox = GearboxConfig(**data["gearbox"])
        if "shredder" in data: config.shredder = ShredderConfig(**data["shredder"])
        if "material" in data: config.material = MaterialProperties(**data["material"])
        if "bearing" in data: config.bearing = BearingConfig(**data["bearing"])

        return config

# Default configuration instance
default_config = ShredderSystemConfig()
