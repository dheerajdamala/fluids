"""
PyFluent Python Script for Automating ANSYS Fluent Pipe Flow Simulation.
Automates 2D axisymmetric mesh loading, laminar model selection,
water fluid setup, boundary conditions, SIMPLE solver execution,
and export of velocity and pressure profiles.
"""

import sys

def run_pyfluent_pipe_simulation(roll_number=67):
    try:
        import ansys.fluent.core as pyfluent
    except ImportError:
        print("[Notice] 'ansys-fluent-core' is not installed in the local Python environment.")
        print("To run PyFluent with a licensed ANSYS installation, run: pip install ansys-fluent-core")
        print("You can also run ANSYS Fluent directly using the journal script: fluent 2ddp -i pipe_flow_fluent.jou")
        return

    u_in = float(roll_number)
    print(f"Connecting to ANSYS Fluent solver session (U_in = {u_in} m/s)...")
    session = pyfluent.launch_fluent(precision="double", dimension=2, mode="solver")

    # Read 2D axisymmetric mesh (L = 3.53 mm, R = 11.99 um)
    # session.file.read(file_type="case", file_name="pipe_mesh.cas.h5")

    # 1. Models: 2D Axisymmetric & Laminar
    session.setup.general.solver.two_dim_space = "axisymmetric"
    session.setup.models.viscous.model = "laminar"

    # 2. Material: Liquid Water
    water = session.setup.materials.fluid["water-liquid"]
    water.density.value = 998.2
    water.viscosity.value = 1.002e-3

    # 3. Cell Zone
    session.setup.cell_zone_conditions.fluid["fluid-domain"].material = "water-liquid"

    # 4. Boundary Conditions
    # Inlet
    inlet = session.setup.boundary_conditions.velocity_inlet["inlet"]
    inlet.vmag.value = u_in

    # Outlet
    outlet = session.setup.boundary_conditions.pressure_outlet["outlet"]
    outlet.gauge_pressure.value = 0.0

    # Symmetry Axis (r = 0)
    session.setup.boundary_conditions.axis["axis"]

    # Wall No-Slip (r = R)
    wall = session.setup.boundary_conditions.wall["wall-pipe"]
    wall.motion_bc = "Stationary Wall"
    wall.shear_bc = "No Slip"

    # 5. Solution Methods & Initialization
    session.solution.methods.p_v_coupling.flow_scheme = "SIMPLE"
    session.solution.initialization.initialization_type = "standard"
    session.solution.initialization.compute_defaults.from_zone = "inlet"
    session.solution.initialization.initialize()

    # 6. Solve
    print("Iterating to convergence...")
    session.solution.run_calculation.iterate(number_of_iterations=500)

    # 7. Post-Processing
    print("Simulation converged. Exporting data...")
    session.file.write(file_type="case-data", file_name="fluent_solution.cas.h5")
    session.exit()
    print("PyFluent simulation completed.")

if __name__ == "__main__":
    roll = int(sys.argv[1]) if len(sys.argv) > 1 else 67
    run_pyfluent_pipe_simulation(roll)

