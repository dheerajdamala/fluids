"""
CLI Execution Script for Water Pipe Flow Simulation.
Calculates laminar pipe parameters based on roll number,
runs numerical solver, generates publication-quality figures,
and exports data tables.
"""

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pipe_flow_simulation import PipeFlowSimulation

def plot_all_results(sim, output_dir="results", show=False):
    os.makedirs(output_dir, exist_ok=True)
    plt.rcParams.update({'font.size': 10, 'font.family': 'sans-serif'})

    # ------------------ Plot 1: 2D Axisymmetric Velocity Contour ------------------
    fig, ax = plt.subplots(figsize=(12, 4))
    
    # Mirror across axis of symmetry to display full pipe cross-section (-R to +R)
    r_full = np.concatenate([-sim.r[::-1], sim.r[1:]]) * 1e6  # in micrometers
    u_full = np.concatenate([sim.u[:, ::-1], sim.u[:, 1:]], axis=1)
    X_mesh, R_mesh = np.meshgrid(sim.x * 1e3, r_full)  # x in mm, r in um

    levels = np.linspace(0, np.max(sim.u), 40)
    cf = ax.contourf(X_mesh, R_mesh, u_full.T, levels=levels, cmap="turbo")
    cbar = plt.colorbar(cf, ax=ax, pad=0.02)
    cbar.set_label("Axial Velocity $u(x, r)$ [m/s]", fontsize=10, fontweight="bold")

    # Mark the entrance length Le
    ax.axvline(x=sim.Le * 1e3, color="white", linestyle="--", linewidth=1.8, label=f"Entrance Length $L_e = {sim.Le*1e3:.2f}$ mm")
    ax.axhline(y=0, color="gray", linestyle=":", linewidth=0.8, alpha=0.7, label="Centerline (Axis of Symmetry)")

    # Add text annotations for regions
    ax.text(sim.Le * 0.45 * 1e3, sim.R * 0.65 * 1e6, "DEVELOPING REGION\n(Growing Boundary Layer)",
            color="white", fontweight="bold", fontsize=9, ha="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.6))
    ax.text((sim.Le + (sim.L - sim.Le)*0.5) * 1e3, sim.R * 0.65 * 1e6, "FULLY DEVELOPED REGION\n(Hagen-Poiseuille)",
            color="white", fontweight="bold", fontsize=9, ha="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.6))

    ax.set_title(f"2D Axial Velocity Field $u(x, r)$ for Water Flow in Pipe ($U_{{in}} = {sim.U_in}$ m/s, $Re = {sim.Re:.0f}$)",
                 fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel("Axial Distance along Pipe $x$ [mm]", fontweight="bold")
    ax.set_ylabel("Radial Coordinate $r$ [$\\mu$m]", fontweight="bold")
    ax.legend(loc="lower right", framealpha=0.85)
    plt.tight_layout()
    contour_path = os.path.join(output_dir, "velocity_contour.png")
    plt.savefig(contour_path, dpi=300)
    print(f"Saved: {contour_path}")
    if show: plt.show()
    plt.close()

    # ------------------ Plot 2: Radial Velocity Profiles at Axial Stations ------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Pick representative stations: entrance, early developing, mid, Le, fully developed
    stations_ratios = [0.0, 0.05, 0.20, 0.50, 1.00, 1.50]
    colors = plt.cm.plasma(np.linspace(0.1, 0.9, len(stations_ratios)))

    for ratio, col in zip(stations_ratios, colors):
        target_x = ratio * sim.Le
        idx = min(int(round((target_x / sim.L) * (sim.Nx - 1))), sim.Nx - 1)
        actual_x = sim.x[idx]
        actual_ratio = actual_x / sim.Le
        label_text = f"$x/L_e = {actual_ratio:.2f}$ ({actual_x*1e3:.2f} mm)"
        if ratio == 0.0:
            label_text = "Inlet ($x=0$, Slug Flow)"
        elif ratio == 1.00:
            label_text = f"Entrance ($x = L_e = {sim.Le*1e3:.2f}$ mm)"
        
        ax.plot(sim.u[idx, :], sim.r / sim.R, label=label_text, color=col, linewidth=2.0)

    # Theoretical Poiseuille parabolic profile
    u_poiseuille = sim.analytical_poiseuille_profile()
    ax.plot(u_poiseuille, sim.r / sim.R, "k--", linewidth=2.2, label="Theoretical Hagen-Poiseuille ($2 U_{in}(1 - r^2/R^2)$)")

    ax.set_title("Evolution of Radial Velocity Profiles from Inlet to Fully Developed State", fontweight="bold", fontsize=11)
    ax.set_xlabel("Axial Velocity $u(r)$ [m/s]", fontweight="bold")
    ax.set_ylabel("Non-Dimensional Radial Position $r / R$", fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="lower left", framealpha=0.9)
    plt.tight_layout()
    profiles_path = os.path.join(output_dir, "velocity_profiles.png")
    plt.savefig(profiles_path, dpi=300)
    print(f"Saved: {profiles_path}")
    if show: plt.show()
    plt.close()

    # ------------------ Plot 3: Centerline Velocity Acceleration uc(x)/Uin ------------------
    fig, ax = plt.subplots(figsize=(9, 5))
    x_norm = sim.x / sim.Le
    uc_norm = sim.u_centerline / sim.U_in

    ax.plot(x_norm, uc_norm, "b-", linewidth=2.5, label="Numerical CFD Solution ($u_c(x) / U_{in}$)")
    ax.axhline(y=2.0, color="r", linestyle="--", linewidth=1.8, label="Theoretical Developed Asymptote ($u_{max}/U_{in} = 2.0$)")
    ax.axvline(x=1.0, color="g", linestyle=":", linewidth=1.8, label="Entrance Length Threshold ($x = L_e$)")
    ax.axhline(y=1.98, color="orange", linestyle="--", alpha=0.7, label="99% Fully Developed Threshold ($1.98$)")

    ax.set_title("Centerline Velocity Development: $u_c(x) / U_{in}$ vs Normalized Axial Distance $x / L_e$", fontweight="bold", fontsize=11)
    ax.set_xlabel("Normalized Distance along Pipe $x / L_e$", fontweight="bold")
    ax.set_ylabel("Centerline Velocity Ratio $u_c / U_{in}$", fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="lower right", framealpha=0.9)
    plt.tight_layout()
    centerline_path = os.path.join(output_dir, "centerline_velocity.png")
    plt.savefig(centerline_path, dpi=300)
    print(f"Saved: {centerline_path}")
    if show: plt.show()
    plt.close()

    # ------------------ Plot 4: Pressure Drop & Apparent Friction Factor ------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Pressure Drop (kPa or MPa)
    p_drop_kPa = (sim.p[0] - sim.p) / 1e3
    ax1.plot(sim.x * 1e3, p_drop_kPa, "purple", linewidth=2.2, label="Numerical Pressure Drop $\\Delta P(x)$")
    
    # Linear Hagen-Poiseuille pressure drop reference
    dp_linear = -sim.dp_dx_theoretical * sim.x / 1e3
    ax1.plot(sim.x * 1e3, dp_linear, "k--", linewidth=1.5, label="Fully Developed Linear Poiseuille Slope")
    ax1.axvline(x=sim.Le * 1e3, color="g", linestyle=":", linewidth=1.5, label="Entrance Length $L_e$")

    ax1.set_title("Axial Pressure Drop $\\Delta P(x)$ along Pipe", fontweight="bold")
    ax1.set_xlabel("Axial Position $x$ [mm]", fontweight="bold")
    ax1.set_ylabel("Cumulative Pressure Drop $\\Delta P$ [kPa]", fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.6)
    ax1.legend(loc="upper left")

    # Apparent friction factor product f_app * Re
    valid_idx = np.where(x_norm > 0.02)[0]
    f_Re = sim.f_apparent[valid_idx] * sim.Re
    ax2.plot(x_norm[valid_idx], f_Re, "teal", linewidth=2.2, label="Numerical $f_{app} \\cdot Re$")
    ax2.axhline(y=64.0, color="r", linestyle="--", linewidth=1.8, label="Poiseuille Constant ($f \\cdot Re = 64$)")
    ax2.axvline(x=1.0, color="g", linestyle=":", linewidth=1.5, label="$x / L_e = 1.0$")

    ax2.set_title("Apparent Friction Factor Product $f_{app} \\cdot Re$", fontweight="bold")
    ax2.set_xlabel("Normalized Distance $x / L_e$", fontweight="bold")
    ax2.set_ylabel("$f_{app} \\cdot Re$", fontweight="bold")
    ax2.set_ylim(50, 120)
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(loc="upper right")

    plt.tight_layout()
    pressure_path = os.path.join(output_dir, "pressure_drop.png")
    plt.savefig(pressure_path, dpi=300)
    print(f"Saved: {pressure_path}")
    if show: plt.show()
    plt.close()

    # ------------------ Plot 5: Wall Shear Stress ------------------
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(sim.x * 1e3, sim.tau_w / 1e3, "crimson", linewidth=2.2, label="Numerical Wall Shear $\\tau_w(x)$")
    ax.axhline(y=sim.tau_w_theoretical / 1e3, color="k", linestyle="--", linewidth=1.8, label=f"Theoretical Poiseuille $\\tau_w = {sim.tau_w_theoretical/1e3:.2f}$ kPa")
    ax.axvline(x=sim.Le * 1e3, color="g", linestyle=":", linewidth=1.8, label="Entrance Length $L_e$")

    ax.set_title("Wall Shear Stress $\\tau_w(x)$ Development (Entrance Effect to Poiseuille)", fontweight="bold")
    ax.set_xlabel("Axial Distance along Pipe $x$ [mm]", fontweight="bold")
    ax.set_ylabel("Wall Shear Stress $\\tau_w$ [kPa]", fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="upper right")
    plt.tight_layout()
    shear_path = os.path.join(output_dir, "wall_shear_stress.png")
    plt.savefig(shear_path, dpi=300)
    print(f"Saved: {shear_path}")
    if show: plt.show()
    plt.close()


def export_csv_summary(sim, filepath="results/simulation_summary.csv"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    summary = sim.summary()
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# Pipe Flow Simulation Physics Summary\n")
        for k, v in summary.items():
            f.write(f"{k},{v}\n")
        f.write("\n# Centerline and Axial Development Data\n")
        f.write("x_mm,x_over_Le,uc_mps,uc_over_Uin,delta_P_kPa,tau_w_kPa,f_app_Re\n")
        for i in range(sim.Nx):
            x_mm = sim.x[i] * 1e3
            x_Le = sim.x[i] / sim.Le
            uc = sim.u_centerline[i]
            uc_ratio = uc / sim.U_in
            dP = (sim.p[0] - sim.p[i]) / 1e3
            tau = sim.tau_w[i] / 1e3
            fRe = sim.f_apparent[i] * sim.Re
            f.write(f"{x_mm:.4f},{x_Le:.4f},{uc:.4f},{uc_ratio:.4f},{dP:.4f},{tau:.4f},{fRe:.4f}\n")
    print(f"Summary data exported to: {filepath}")


def print_report_table(sim):
    summary = sim.summary()
    print("\n" + "=" * 75)
    print("      LAMINAR PIPE FLOW NUMERICAL SIMULATION - ENGINEERING SUMMARY")
    print("=" * 75)
    for k, v in summary.items():
        if isinstance(v, float):
            print(f"  {k:<42} : {v:.4f}")
        else:
            print(f"  {k:<42} : {v}")
    print("=" * 75 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Simulate Water Flow in Pipe (Developing & Fully Developed Laminar)")
    parser.add_argument("--roll-number", type=int, default=67, help="Last two digits of roll number (sets U_in in m/s)")
    parser.add_argument("--reynolds", type=float, default=1600.0, help="Target Reynolds number (< 2300 for laminar)")
    parser.add_argument("--nr", type=int, default=100, help="Number of radial grid points")
    parser.add_argument("--nx", type=int, default=400, help="Number of axial grid stations")
    parser.add_argument("--output-dir", type=str, default="results", help="Directory to save figures and CSV")
    parser.add_argument("--show-plots", action="store_true", help="Display Matplotlib plot windows")

    args = parser.parse_args()

    print(f"Initializing simulation for Roll Number: {args.roll_number} (U_in = {args.roll_number} m/s)...")
    sim = PipeFlowSimulation(
        roll_number=args.roll_number,
        target_re=args.reynolds,
        nr=args.nr,
        nx=args.nx
    )

    print(f"Calculated Laminar Pipe Diameter D: {sim.D*1e6:.2f} um ({sim.D*1e3:.4f} mm)")
    print(f"Hydrodynamic Entrance Length Le:   {sim.Le*1e3:.3f} mm")
    print(f"Total Pipe Length L (1.6 * Le):    {sim.L*1e3:.3f} mm")
    print("Executing 2D Axisymmetric Implicit Navier-Stokes marching solver...")

    sim.solve()
    print("Solver completed successfully!")

    print_report_table(sim)
    plot_all_results(sim, output_dir=args.output_dir, show=args.show_plots)
    export_csv_summary(sim, filepath=os.path.join(args.output_dir, "simulation_summary.csv"))

if __name__ == "__main__":
    main()

