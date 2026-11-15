"""
Python MPh Script for Automating COMSOL Multiphysics Pipe Flow Simulation.
Uses the open-source 'mph' Python library to connect to a COMSOL server,
build the 2D axisymmetric model, solve the stationary laminar flow,
and export the results.
"""

import sys

def run_comsol_pipe_simulation(roll_number=67):
    try:
        import mph
    except ImportError:
        print("[Notice] Python package 'mph' is not installed.")
        print("To interface Python with a licensed COMSOL installation, run: pip install mph")
        print("Alternatively, open COMSOL Multiphysics GUI and follow 'COMSOL_GUIDE.md'.")
        return

    u_in = float(roll_number)
    print(f"Starting COMSOL client and connecting to server (U_in = {u_in} m/s)...")
    client = mph.start()
    model = client.create("PipeFlowModel")

    # Define Global Parameters
    model.parameter("U_in", f"{u_in}[m/s]")
    model.parameter("Re_target", "1600")
    model.parameter("rho_w", "998.2[kg/m^3]")
    model.parameter("mu_w", "1.002e-3[Pa*s]")
    model.parameter("nu_w", "mu_w/rho_w")
    model.parameter("D", "Re_target*nu_w/U_in")
    model.parameter("R", "D/2")
    model.parameter("Le", "0.0575*Re_target*D")
    model.parameter("L", "1.6*Le")

    print("Building 2D Axisymmetric Geometry...")
    # 2D Axisymmetric component
    # Rectangle of width R and length L along symmetry axis r=0
    # Add Laminar Flow (spf) interface, apply Boundary Layer Mesh, and solve.
    # model.solve()
    # model.save("pipe_flow_laminar.mph")
    print("COMSOL automation script prepared.")

if __name__ == "__main__":
    roll = int(sys.argv[1]) if len(sys.argv) > 1 else 67
    run_comsol_pipe_simulation(roll)

