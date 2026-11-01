import sys
import os
import math
import numpy as np

try:
    from parameters.shredder_config import ShredderSystemConfig, default_config
except ImportError:
    # Add parameters directory to sys.path if running as script
    sys.path.append(os.path.join(os.path.dirname(__file__), 'parameters'))
    from shredder_config import ShredderSystemConfig, default_config

# Import skfem
try:
    from skfem import *
    from skfem.helpers import dot, grad
    # from skfem.models.poisson import poisson, unit_load # Not needed as we define custom forms
    HAS_SKFEM = True
except ImportError as e:
    HAS_SKFEM = False
    print(f"Warning: scikit-fem not found. Error: {e}")
    print("Using analytical approximation.")

class StressSimulator:
    def __init__(self, config: ShredderSystemConfig):
        self.config = config

    def simulate_torsion(self, verbose=False):
        """
        Simulates torsion on the output shaft using 2D FEM (Prandtl Stress Function)
        or analytical approximation if FEM fails/missing.
        """
        motor = self.config.motor
        gearbox = self.config.gearbox
        material = self.config.material

        # 1. Load Parameters
        torque = motor.torque_nm * gearbox.ratio # Max possible torque
        hex_flat_to_flat = gearbox.output_shaft_hex_mm

        # Radius of circumcircle for Hex
        # Flat = sqrt(3) * R => R = Flat / sqrt(3)
        R = hex_flat_to_flat / math.sqrt(3)

        # 2. FEM Simulation (if available)
        if HAS_SKFEM:
            try:
                max_stress_normalized = self._solve_fem_torsion(R)
                # Prandtl stress function u satisfies div(grad(u)) = -2G*theta
                # Stress components: tau_xz = dphi/dy, tau_yz = -dphi/dx
                # Torque T = 2 * Integral(u) dA
                # We solved -div(grad(u)) = 2 (Normalized)
                # Let's say we solved for u_norm.
                # T_norm = 2 * Integral(u_norm) dA
                # Scaling factor: T_actual / T_norm.
                # Stress_actual = Stress_norm * (T_actual / T_norm)

                # Wait, the scaling is linear.
                # max_shear_stress = (Max_Grad_u_norm / T_norm) * Torque_actual?
                # Yes.

                max_shear_stress = max_stress_normalized * torque

                if verbose:
                    print(f"FEM Max Shear Stress: {max_shear_stress/1e6:.2f} MPa")

            except Exception as e:
                print(f"FEM failed: {e}. Falling back to analytical.")
                max_shear_stress = self._analytical_torsion(hex_flat_to_flat, torque)
        else:
            max_shear_stress = self._analytical_torsion(hex_flat_to_flat, torque)

        # 3. Safety Factor
        # Von Mises Yield Criterion for pure shear: Tau_yield = Yield / sqrt(3)
        yield_strength = material.shaft_yield_strength_mpa * 1e6 # Pa
        shear_yield = yield_strength / math.sqrt(3)

        safety_factor = shear_yield / max_shear_stress if max_shear_stress > 0 else 999.0

        return {
            "max_shear_stress_mpa": max_shear_stress / 1e6,
            "safety_factor": safety_factor,
            "torque_nm": torque
        }

    def _analytical_torsion(self, s, T):
        """
        Approximate max shear stress for a hexagonal shaft.
        Formula: Tau_max = T / (0.208 * s^3) approx for hex?
        Actually, for regular polygons:
        Tau_max = T * R / J_eff ?
        Let's use a known approx for Hexagon.
        Polar Moment of Inertia J = 0.121 * s^4 ? (s = side length)
        Wait, let's look up specific formula.
        For Hexagon of side 'a' (radius R):
        J ~ 5sqrt(3)/16 * a^4 ?

        Let's use the standard "Polar Modulus" Z_p.
        Tau = T / Z_p.
        For Hexagon with flat-to-flat 'd' (d = s in our config):
        Z_p approx 0.208 * d^3 (Similar to square 0.208*d^3).
        Actually for Square it's T / (0.208 a^3).
        For Hexagon, it's closer to Circle.
        Circle: Z_p = pi * d^3 / 16 ~ 0.196 d^3.
        So 0.208 is conservative? No, circle is most efficient.
        Hexagon is less efficient than circle of same diameter?
        Actually Hexagon flat-to-flat 'd' fits inside circle of diameter 'D' > 'd'.

        Let's use conservative circular approximation with diameter = flat-to-flat (inner circle).
        Tau = 16 * T / (pi * d^3)
        This assumes the shaft is a cylinder of diameter 'd' (smallest dimension).
        The corners carry less stress usually in torsion? No, midpoints of flats carry MAX stress in non-circular torsion.
        So the inner circle approximation is actually usually correct for max stress location!

        Max stress occurs at the closest point to center (midpoint of flat).
        So Tau_max ~ T / Z_p_inscribed.
        """
        d = s / 1000.0 # convert mm to m
        # Polar section modulus of inscribed circle
        Z_p = (math.pi * d**3) / 16.0
        return T / Z_p

    def _solve_fem_torsion(self, R_mm):
        """
        Solves the Poisson equation -div(grad(u)) = 2 on a Hexagon.
        Returns (Max_Stress / Torque_factor) ratio.
        """
        R = R_mm / 1000.0 # meters

        # 1. Generate Mesh
        # Create a Hexagon centered at 0,0 with radius R
        # We can use MeshTri.init_circle? No.
        # Let's create points manually.
        angles = np.linspace(0, 2*np.pi, 7)[:-1]
        pts = np.vstack([R * np.cos(angles), R * np.sin(angles)])
        # Add center
        pts = np.hstack([[[0],[0]], pts]) # 0 is center, 1..6 are corners

        # Triangles: (0, 1, 2), (0, 2, 3), ... (0, 6, 1)
        tris = np.array([
            [0, 1, 2],
            [0, 2, 3],
            [0, 3, 4],
            [0, 4, 5],
            [0, 5, 6],
            [0, 6, 1]
        ]).T

        m = MeshTri(pts, tris)
        # Refine mesh for accuracy
        m = m.refined(3)

        # 2. Define Problem
        # -div(grad(u)) = 2
        # u = 0 on boundary (Dirichlet)

        basis = Basis(m, ElementTriP1())

        # Bilinear form (Laplacian)
        # a(u, v) = integral(grad(u) . grad(v))
        # Use skfem's simplified interface

        # Weak form: \int grad(u).grad(v) dx = \int 2v dx

        @BilinearForm
        def laplace(u, v, w):
            return dot(grad(u), grad(v))

        @LinearForm
        def load(v, w):
            return 2.0 * v

        A = laplace.assemble(basis)
        b = load.assemble(basis)

        # Boundary conditions (u=0 on boundary)
        D = basis.get_dofs()
        u = solve(*condense(A, b, D=D))

        # 3. Calculate Properties
        # Torque T = 2 * Integral(u)
        # We need to integrate the solution u over the domain.

        @Functional
        def integrate_u(w):
            return w['u']

        # Or simpler: L2 projection? No.
        # Just integrate u.
        # skfem has functionals.

        # T_norm = 2 * \int u dA
        # We can use the basis to integrate.
        # Interpolate u to integration points?

        # Let's use a Functional form
        @Functional
        def integral_u(w):
            return w.u

        T_norm = 2.0 * integral_u.assemble(basis, u=u)

        # 4. Calculate Max Stress
        # Stress vector tau = [-du/dy, du/dx] (rotated gradient)
        # Magnitude = |grad(u)|
        # We need max(|grad(u)|)

        # Evaluate gradient at quadrature points
        # grad(u) is constant on P1 elements? Yes.
        # So we can just get gradients on elements.

        # basis.interpolate(u) gives DiscreteField
        # .grad gives gradients at quadrature points

        interp = basis.interpolate(u)
        grads = interp.grad # shape (2, n_quad, n_elems)

        # Magnitude squared
        grad_sq = grads[0]**2 + grads[1]**2
        grad_mag = np.sqrt(grad_sq)

        max_grad = np.max(grad_mag)

        # Return factor: Max_Stress / Torque
        # Stress = (Grad / T_norm) * T_actual
        # So we return Max_Grad / T_norm

        return max_grad / T_norm

if __name__ == "__main__":
    print("Running Stress Simulation...")

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

    sim = StressSimulator(cfg)
    results = sim.simulate_torsion(verbose=True)

    print("\n--- Simulation Report ---")
    print(f"Torque Load: {results['torque_nm']:.2f} Nm")
    print(f"Max Shear Stress: {results['max_shear_stress_mpa']:.2f} MPa")
    print(f"Safety Factor: {results['safety_factor']:.2f}")
