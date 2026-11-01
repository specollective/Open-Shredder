# OpenShredder Project Roadmap

This document tracks the ongoing development, optimization, and future feature requests for the OpenShredder project.

## 1. Mechanical Design (Build123d)

### Completed
- [x] **Parametric Gearbox:** Centralized configuration (`shredder_config.json`) for gear ratio, housing dimensions, and shaft sizes.
- [x] **End-to-End Validation:** Script (`validate_design.py`) to check geometric fit and torque requirements.
- [x] **Stress Simulation:** FEA-based torsion simulation (`simulate_stress.py`) for the hexagonal output shaft.
- [x] **Design Optimization Agent:** Automated script (`optimize_design.py`) to tune parameters for maximum throughput/safety.
- [x] **Full Assembly Generation:** `full_machine_assembly.py` generates the complete machine STEP file based on the optimized config.

### In Progress / TODO
- [ ] **Hopper Design:** The current `pusher_mechanism.py` is a placeholder. A full hopper with guide rails is needed.
- [ ] **Bearing Integration:** Explicitly model bearing pockets and select standard bearings (e.g., 6000 series) in the configuration.
- [ ] **Helical Gear Profile:** The current cycloidal drive uses straight pins. Evaluate helical or double-cycloid for smoother operation/noise reduction.
- [ ] **Fastener Library:** Add bolts, nuts, and washers to the assembly script for a complete BOM.
- [ ] **Frame/Stand:** Design a parametric frame (aluminum extrusion or welded steel) to mount the gearbox and motor.

## 2. Simulation & Analysis

### Completed
- [x] **Torsion FEA:** 2D Poisson solver for hexagonal shaft torsion.

### In Progress / TODO
- [ ] **Bending Moment Analysis:** The shaft also experiences bending from the shredding force. Update `simulate_stress.py` to include bending + torsion (Von Mises stress).
- [ ] **Tooth Strength Analysis:** Simulate the stress on the shredder teeth/inserts to prevent fracture.
- [ ] **Jamming Simulation:** Create a dynamic simulation (time-stepped) to model potential jam scenarios and test the "Impact Drive" effectiveness.
- [ ] **Thermal Analysis:** Estimate heat generation in the gearbox/motor for continuous duty cycles.

## 3. Firmware (Arduino Motor Controller)

### Completed
- [x] **Basic Motor Control:** Stepper and DC motor support.
- [x] **Jam Detection:** Current monitoring and auto-reverse logic.

### In Progress / TODO
- [ ] **Load-Dependent Speed Control:** Automatically reduce speed (increase torque) when current spikes, before a full jam occurs.
- [ ] **Impact Mode Tuning:** Refine the "back-off and strike" algorithm parameters based on real-world testing.
- [ ] **User Interface:** Add a simple LCD/OLED menu to configure settings (e.g., reverse time, current limit) without reflashing.
- [ ] **Telemetry:** Output real-time current/RPM data to serial for analysis/digital twin verification.

## 4. Documentation

### Completed
- [x] **Workflow Documentation:** Updated `Mechanics/Build123d_Gearbox/README.md` with new validation/optimization steps.

### In Progress / TODO
- [ ] **Assembly Manual:** Step-by-step PDF or Wiki for assembling the physical hardware.
- [x] **Bill of Materials (BOM):** Auto-generate a CSV BOM from the python scripts (`generate_bom.py`).
- [ ] **Tuning Guide:** Instructions on how to interpret validation errors and manually tune the `shredder_config.json`.
