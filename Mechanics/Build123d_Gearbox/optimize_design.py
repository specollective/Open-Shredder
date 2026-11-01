import sys
import os
import copy
import random
import math
from dataclasses import asdict

try:
    from parameters.shredder_config import ShredderSystemConfig, default_config
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'parameters'))
    from shredder_config import ShredderSystemConfig, default_config

from validate_design import validate_config, DesignValidator
from simulate_stress import StressSimulator

class DesignOptimizerAgent:
    def __init__(self, initial_config: ShredderSystemConfig):
        self.current_config = copy.deepcopy(initial_config)
        self.best_config = copy.deepcopy(initial_config)
        self.best_score = -float('inf')
        self.history = []

    def evaluate(self, config: ShredderSystemConfig):
        """
        Evaluates the configuration.
        Returns a score (higher is better).
        """
        # 1. Validation (Hard Constraints)
        validator = DesignValidator(config)
        valid = validator.run()

        if not valid:
            # Penalize errors heavily
            return -1000.0 - (len(validator.errors) * 100)

        # 2. Simulation (Soft Constraints & Objectives)
        sim = StressSimulator(config)
        try:
            # Suppress verbose output during optimization
            results = sim.simulate_torsion(verbose=False)
        except Exception:
            return -2000.0 # Simulation crash

        safety_factor = results['safety_factor']
        torque = results['torque_nm']

        # Calculate Required Torque (re-logic from validator or shared?)
        # Ideally shared. For now, let's grab it from validator if possible or re-calc.
        # Validator doesn't store required torque publicly easily.
        # Let's re-calc briefly or trust validator passed.

        # If validator passed, we know Torque >= Required (roughly).
        # But we want to maximize RPM?

        motor_rpm = config.motor.max_rpm
        ratio = config.gearbox.ratio
        output_rpm = motor_rpm / ratio

        # Objective: Maximize RPM while maintaining SF > 1.5
        # Also maybe minimize weight (shaft size)?

        score = output_rpm

        # Safety Factor Bonus/Penalty
        if safety_factor < 1.5:
            score -= 500.0 # Penalty for low safety factor (even if validator didn't catch it as error yet)
        else:
            score += min(safety_factor, 10.0) * 0.1 # Small bonus for robustness

        return score

    def perturb(self, config: ShredderSystemConfig):
        """
        Intelligently modifies the configuration based on errors, or explores randomly.
        """
        new_config = copy.deepcopy(config)

        # Check current errors to guide perturbation
        validator = DesignValidator(config)
        validator.check_geometry()
        validator.check_mechanics()

        errors = validator.errors
        fixed_something = False

        # Heuristic 1: Fix Shaft Length
        if any("Shaft too short" in e for e in errors):
            stack_len = new_config.shredder.num_disks * new_config.shredder.disk_thickness_mm
            new_config.gearbox.output_shaft_length_mm = stack_len + 30.0
            fixed_something = True

        # Heuristic 2: Fix Torque (Increase Ratio)
        if any("Insufficient Torque" in e for e in errors):
            new_config.gearbox.ratio *= 1.2 # Increase by 20%
            fixed_something = True

        # If no obvious errors, explore randomly
        if not fixed_something:
            choice = random.choice(['ratio', 'shaft_hex', 'drum_dia'])

            if choice == 'ratio':
                # Gear Ratio: 5.0 to 100.0
                current = new_config.gearbox.ratio
                delta = random.uniform(-2.0, 2.0)
                new_config.gearbox.ratio = max(5.0, min(100.0, current + delta))

            elif choice == 'shaft_hex':
                # Shaft Hex: 15mm to 40mm
                current = new_config.gearbox.output_shaft_hex_mm
                delta = random.choice([-1.0, 1.0])
                new_val = max(15.0, min(40.0, current + delta))
                new_config.gearbox.output_shaft_hex_mm = new_val
                new_config.shredder.hex_bore_mm = new_val

            elif choice == 'drum_dia':
                 # Drum Dia: 100mm to 200mm
                 current = new_config.shredder.drum_diameter_mm
                 delta = random.uniform(-5.0, 5.0)
                 new_config.shredder.drum_diameter_mm = max(100.0, min(200.0, current + delta))

        return new_config

    def run(self, steps=50):
        print(f"Starting Optimization for {steps} steps...")

        # Initial Eval
        current_score = self.evaluate(self.current_config)
        self.best_score = current_score
        print(f"Initial Score: {current_score:.2f}")

        for i in range(steps):
            new_config = self.perturb(self.current_config)
            score = self.evaluate(new_config)

            # Simple Hill Climbing (Accept if better)
            # Or Simulated Annealing?
            # Let's use simple greedy with restart?
            # Greedy:
            if score >= self.best_score:
                if score > self.best_score:
                    print(f"Step {i}: Improved! Score: {score:.2f} (Ratio: {new_config.gearbox.ratio:.1f}, Hex: {new_config.gearbox.output_shaft_hex_mm}mm)")
                self.best_score = score
                self.best_config = new_config
                self.current_config = new_config
            else:
                # Restart from best
                self.current_config = self.best_config

        print("Optimization Complete.")
        return self.best_config

if __name__ == "__main__":
    # Load default
    config_path = os.path.join(os.path.dirname(__file__), 'parameters', 'shredder_config.json')
    if os.path.exists(config_path):
        cfg = ShredderSystemConfig.load_from_json(config_path)
    else:
        cfg = default_config

    agent = DesignOptimizerAgent(cfg)
    optimized_cfg = agent.run(steps=100)

    # Save optimized
    optimized_path = os.path.join(os.path.dirname(__file__), 'parameters', 'optimized_shredder_config.json')
    optimized_cfg.save_to_json(optimized_path)
    print(f"Saved optimized config to {optimized_path}")

    # Run validation on final
    print("\nFinal Validation:")
    validate_config(optimized_cfg)
