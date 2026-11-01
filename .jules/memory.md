## Archived: 2026-10-31

* The project utilizes `scikit-fem`, `meshio`, `numpy`, and `scipy` to perform mechanical stress simulations (FEA) on the driveshaft, with an implemented analytical fallback.
* Future project development tasks are tracked in `TODO.md`.
* The firmware source code is located in `Firmware/Arduino_Motor_Controller`.
* The `build123d` scripts for the gearbox and impact drive are located in `Mechanics/Build123d_Gearbox/`.
* The project prioritizes indoor home use, requiring minimized noise levels.
* The system power source is defined as 110V AC, to be utilized via appropriate motor drivers.
* The 'scripted' functionality refers to a standalone sequence mode (e.g., Run -> Pause -> Repeat) rather than remote control via host.
* Jam detection relies on current monitoring (for DC) or closed-loop alarm signals (for Steppers) to trigger auto-reverse logic.
* The mechanical gearbox design parameters support NEMA 34 specifications: 69.6mm mounting hole spacing and a 14mm input shaft diameter.
* The motor controller firmware implements a 500ms inrush masking period to ignore current spikes during the initial motor startup.
* The fixed knife bar is designed to be made of plastic (e.g., HDPE) to interface with the toothed groove pattern of the shredder drum.
* All mechanical design parameters are centralized in `Mechanics/Build123d_Gearbox/parameters/shredder_config.json`, which drives the generation scripts.
* The project targets the Arduino hardware platform for motor control.
* An automated optimization workflow (`optimize_design.py`) is used to tune design parameters (Gear Ratio, Shaft Hex, Drum Diameter) to satisfy validation constraints (`validate_design.py`) and maximize throughput.
* The project includes a `generate_bom.py` script that calculates a Bill of Materials (BOM) based on the active configuration, outputting estimated masses for printed parts and quantities for hardware/electronics to `BOM.csv`.
* The system includes an 'Impact Mode' strategy for clearing jams, involving a back-off and strike action.
* The mechanical design includes an impact drive mechanism (slip disk and hammer) to force multiply jam clearing potential.
* The motor control system is designed to support a diversity of options, specifically both Stepper (Step/Dir) and DC (PWM/Dir) motor drivers.
* The primary drive motor selected for the project is a NEMA 34 Stepper Motor, chosen for high torque, quiet operation, and compatibility with the 3D-printed gearbox.
* The shredder drum dimensions and shaft size are parametric and controlled by the configuration system; the optimized configuration prefers a 36mm hex shaft and ~132mm drum diameter.
* The project uses `build123d` for scripting parametric 3D models, specifically for the gearbox.
