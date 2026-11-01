# OpenShredder Gearbox & Components (Build123d)

This directory contains Python scripts to generate the 3D models for the OpenShredder gearbox and shredder mechanism using [build123d](https://github.com/gumyr/build123d).

## Prerequisites

You need `build123d` and `scikit-fem` installed:
```bash
pip install build123d scikit-fem meshio numpy scipy
```

## Parameter Configuration

All design parameters are centralized in `parameters/shredder_config.json`.
You can modify this file directly, or use the Optimization Agent to tune it.

## New Workflow: Validation & Optimization

We have implemented an AI-driven optimization loop to ensure the design is mechanically sound.

### 1. Validate Design
Checks geometric constraints (e.g., shaft fit) and mechanical feasibility (torque).
```bash
python3 validate_design.py
```

### 2. Simulate Stress
Runs a Finite Element Analysis (FEA) or analytical simulation to calculate shaft stress and safety factors.
```bash
python3 simulate_stress.py
```

### 3. Optimize Design (Agent)
An intelligent agent that iteratively tweaks parameters (Gear Ratio, Shaft Size, Drum Diameter) to maximize throughput while satisfying safety constraints.
```bash
python3 optimize_design.py
```
This will generate `parameters/optimized_shredder_config.json`.

## Generating Models

The generation scripts automatically load `parameters/optimized_shredder_config.json` if it exists, otherwise they use `parameters/shredder_config.json`.

### Full Assembly
Generates the complete machine model (Gearbox + Shredder + Pusher).
```bash
python3 full_machine_assembly.py
```
- Output: `open_shredder_full_assembly.step`

### Individual Components

- **Gearbox:** `python3 gearbox_assembly.py` -> `shredder_gearbox_assembly.step`
- **Shredder Parts:** `python3 shredder_components.py`
- **Pusher:** `python3 pusher_mechanism.py`

## Scripts Overview

- `parameters/shredder_config.py`: Configuration schema.
- `validate_design.py`: Validation logic.
- `simulate_stress.py`: FEA/Analytical simulation logic.
- `optimize_design.py`: Optimization agent.
- `cycloidal_gear.py`: Generates the core cycloidal disk.
- `impact_drive.py`: Generates the slip-disk and impact hammer mechanism.
- `shredder_components.py`: Generates internal shredder parts.
- `gearbox_assembly.py`: Generates gearbox assembly.
- `full_machine_assembly.py`: Generates full machine assembly.

## Configuration
Adjust parameters in `parameters/shredder_config.json` manually or use `optimize_design.py`.
