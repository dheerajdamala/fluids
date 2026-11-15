"""
Interactive GUI Visualizer for Laminar Pipe Flow Simulation.
Built with Tkinter and Matplotlib (FigureCanvasTkAgg).
Allows interactive parameter adjustment (Roll Number, Reynolds number, grid size),
real-time simulation execution, and interactive graph browsing.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from pipe_flow_simulation import PipeFlowSimulation

class PipeFlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Laminar Pipe Flow CFD Simulator (Developing & Developed Region)")
        self.root.geometry("1200x820")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#1E1E2E")

        self.sim = None
        self._build_ui()
        self.run_sim()

    def _build_ui(self):
        # Top Header
        header = tk.Frame(self.root, bg="#181825", pady=10, padx=15)
        header.pack(fill=tk.X)

        title_box = tk.Frame(header, bg="#181825")
        title_box.pack(side=tk.LEFT)

        title = tk.Label(
            title_box, text="🌊 WATER FLOW IN CIRCULAR PIPE - CFD SIMULATION",
            font=("Segoe UI", 14, "bold"), fg="#89B4FA", bg="#181825"
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            title_box, text="2D Axisymmetric Incompressible Navier-Stokes Solver: Entrance Region to Fully Developed Poiseuille Flow",
            font=("Segoe UI", 9), fg="#BAC2DE", bg="#181825"
        )
        subtitle.pack(anchor="w")

        # Quick Switch to AI Maze Solver Button
        switch_ai_btn = tk.Button(
            header, text="🤖 Switch to AI Maze Solver ➔",
            font=("Segoe UI", 9, "bold"), bg="#A6E3A1", fg="#11111B",
            activebackground="#94E2D5", activeforeground="#11111B",
            relief=tk.FLAT, cursor="hand2", padx=12, pady=6,
            command=self._launch_ai_suite
        )
        switch_ai_btn.pack(side=tk.RIGHT)

        # Main Layout: Left Parameters Sidebar, Right Matplotlib Canvas
        content = tk.Frame(self.root, bg="#1E1E2E")
        content.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # Sidebar
        sidebar = tk.Frame(content, bg="#181825", width=330, padx=12, pady=12)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar.pack_propagate(False)

        # Input Parameters Group
        param_group = tk.LabelFrame(
            sidebar, text=" Input Parameters ",
            font=("Segoe UI", 10, "bold"), fg="#89B4FA", bg="#181825", padx=8, pady=8
        )
        param_group.pack(fill=tk.X, pady=(0, 10))

        # Roll Number / Inlet Velocity
        tk.Label(param_group, text="Roll Number (Last 2 digits = U_in m/s):", font=("Segoe UI", 9), fg="#CDD6F4", bg="#181825").pack(anchor="w", pady=(2, 0))
        self.roll_var = tk.StringVar(value="67")
        self.roll_entry = tk.Entry(param_group, textvariable=self.roll_var, font=("Segoe UI", 10), bg="#313244", fg="#FFFFFF", insertbackground="white")
        self.roll_entry.pack(fill=tk.X, pady=(2, 8))

        # Target Reynolds Number
        tk.Label(param_group, text="Target Reynolds Number Re (< 2300):", font=("Segoe UI", 9), fg="#CDD6F4", bg="#181825").pack(anchor="w")
        self.re_var = tk.StringVar(value="1600")
        self.re_entry = tk.Entry(param_group, textvariable=self.re_var, font=("Segoe UI", 10), bg="#313244", fg="#FFFFFF", insertbackground="white")
        self.re_entry.pack(fill=tk.X, pady=(2, 8))

        # Radial Grid Points Nr
        tk.Label(param_group, text="Radial Grid Points (Nr):", font=("Segoe UI", 9), fg="#CDD6F4", bg="#181825").pack(anchor="w")
        self.nr_var = tk.StringVar(value="80")
        self.nr_entry = tk.Entry(param_group, textvariable=self.nr_var, font=("Segoe UI", 10), bg="#313244", fg="#FFFFFF", insertbackground="white")
        self.nr_entry.pack(fill=tk.X, pady=(2, 8))

        # Axial Grid Stations Nx
        tk.Label(param_group, text="Axial Grid Stations (Nx):", font=("Segoe UI", 9), fg="#CDD6F4", bg="#181825").pack(anchor="w")
        self.nx_var = tk.StringVar(value="300")
        self.nx_entry = tk.Entry(param_group, textvariable=self.nx_var, font=("Segoe UI", 10), bg="#313244", fg="#FFFFFF", insertbackground="white")
        self.nx_entry.pack(fill=tk.X, pady=(2, 8))

        # Run Button
        run_btn = tk.Button(
            sidebar, text="🚀 RUN CFD SIMULATION", font=("Segoe UI", 10, "bold"),
            bg="#A6E3A1", fg="#11111B", activebackground="#94E2D5",
            relief=tk.FLAT, cursor="hand2", pady=6, command=self.run_sim
        )
        run_btn.pack(fill=tk.X, pady=(0, 10))

        # Computed Physics Summary
        summary_group = tk.LabelFrame(
            sidebar, text=" Hydrodynamic Properties ",
            font=("Segoe UI", 9, "bold"), fg="#89B4FA", bg="#181825", padx=8, pady=8
        )
        summary_group.pack(fill=tk.BOTH, expand=True)

        self.summary_text = tk.Text(
            summary_group, font=("Consolas", 8), bg="#181825", fg="#CDD6F4",
            wrap=tk.WORD, relief=tk.FLAT, highlightthickness=0
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True)

        # Right Display Area with Notebook Tabs
        right_panel = tk.Frame(content, bg="#181825")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#181825", borderwidth=0)
        style.configure("TNotebook.Tab", background="#313244", foreground="#CDD6F4", padding=[12, 6], font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#89B4FA")], foreground=[("selected", "#11111B")])

        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: 2D Velocity Contour
        self.tab1 = tk.Frame(self.notebook, bg="#181825")
        self.notebook.add(self.tab1, text="2D Velocity Contour")

        # Tab 2: Velocity Profiles
        self.tab2 = tk.Frame(self.notebook, bg="#181825")
        self.notebook.add(self.tab2, text="Radial Profiles")

        # Tab 3: Centerline Development
        self.tab3 = tk.Frame(self.notebook, bg="#181825")
        self.notebook.add(self.tab3, text="Centerline Velocity uc(x)")

        # Tab 4: Pressure Drop & Friction
        self.tab4 = tk.Frame(self.notebook, bg="#181825")
        self.notebook.add(self.tab4, text="Pressure Drop & Friction")

    def run_sim(self):
        try:
            roll = int(self.roll_var.get())
            re = float(self.re_var.get())
            nr = int(self.nr_var.get())
            nx = int(self.nx_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numerical parameters.")
            return

        if re >= 2300:
            messagebox.showwarning("Reynolds Number Warning", "Re >= 2300 indicates transition to turbulent flow. Choose Re < 2300 for laminar flow.")

        self.sim = PipeFlowSimulation(
            roll_number=roll,
            target_re=re,
            nr=nr,
            nx=nx
        )
        self.sim.solve()
        self._update_summary()
        self._render_tabs()

    def _update_summary(self):
        s = self.sim.summary()
        self.summary_text.delete("1.0", tk.END)
        lines = [
            f"• Inlet Vel U_in : {s['Inlet Velocity U_in (m/s)']:.1f} m/s",
            f"• Reynolds Re    : {s['Target Reynolds Number Re']:.0f} (Laminar)",
            f"• Fluid          : Water (20°C)",
            f"• Density rho    : {s['Density (kg/m3)']:.1f} kg/m³",
            f"• Viscosity mu   : {s['Dynamic Viscosity (Pa.s)']:.3e} Pa·s",
            "--------------------------------",
            f"• Diameter D     : {s['Pipe Diameter D (um)']:.2f} µm",
            f"• Radius R       : {s['Pipe Radius R (um)']:.2f} µm",
            f"• Entrance Le    : {s['Entrance Length Le (mm)']:.3f} mm",
            f"• Total Length L : {s['Total Pipe Length L (mm)']:.3f} mm",
            f"• L / Le Ratio   : {s['L / Le Ratio']:.2f}",
            "--------------------------------",
            f"• Max Vel (CFD)  : {s['Outlet Centerline Velocity (m/s)']:.2f} m/s",
            f"• Max Vel (Exact): {s['Theoretical Fully Developed u_max (m/s)']:.2f} m/s",
            f"• Match Accuracy : {s['Centerline Velocity Accuracy (%)']:.2f}%",
            f"• Wall Shear Tw  : {s['Theoretical Wall Shear Stress (kPa)']:.2f} kPa"
        ]
        self.summary_text.insert(tk.END, "\n".join(lines))

    def _render_tabs(self):
        for tab in [self.tab1, self.tab2, self.tab3, self.tab4]:
            for child in tab.winfo_children():
                child.destroy()

        # Tab 1: Contour
        fig1, ax1 = plt.subplots(figsize=(8.5, 5))
        r_full = np.concatenate([-self.sim.r[::-1], self.sim.r[1:]]) * 1e6
        u_full = np.concatenate([self.sim.u[:, ::-1], self.sim.u[:, 1:]], axis=1)
        X_mesh, R_mesh = np.meshgrid(self.sim.x * 1e3, r_full)
        levels = np.linspace(0, np.max(self.sim.u), 35)
        cf = ax1.contourf(X_mesh, R_mesh, u_full.T, levels=levels, cmap="turbo")
        plt.colorbar(cf, ax=ax1, label="Axial Velocity u(x, r) [m/s]")
        ax1.axvline(x=self.sim.Le * 1e3, color="white", linestyle="--", linewidth=1.5, label=f"Le = {self.sim.Le*1e3:.2f} mm")
        ax1.set_title("2D Axial Velocity Field u(x, r) Contour", fontweight="bold")
        ax1.set_xlabel("Axial Distance x [mm]")
        ax1.set_ylabel("Radial Coordinate r [µm]")
        ax1.legend(loc="lower right")
        fig1.tight_layout()
        self._embed_fig(fig1, self.tab1)

        # Tab 2: Profiles
        fig2, ax2 = plt.subplots(figsize=(8.5, 5))
        for ratio, col in zip([0.0, 0.05, 0.2, 0.5, 1.0, 1.5], plt.cm.plasma(np.linspace(0.1, 0.9, 6))):
            idx = min(int(round((ratio * self.sim.Le / self.sim.L) * (self.sim.Nx - 1))), self.sim.Nx - 1)
            ax2.plot(self.sim.u[idx, :], self.sim.r / self.sim.R, label=f"x/Le = {ratio:.2f}", color=col, linewidth=1.8)
        u_th = self.sim.analytical_poiseuille_profile()
        ax2.plot(u_th, self.sim.r / self.sim.R, "k--", linewidth=2.0, label="Exact Poiseuille")
        ax2.set_title("Radial Velocity Profiles at Axial Stations", fontweight="bold")
        ax2.set_xlabel("Axial Velocity u(r) [m/s]")
        ax2.set_ylabel("Normalized Radius r / R")
        ax2.grid(True, linestyle="--", alpha=0.6)
        ax2.legend()
        fig2.tight_layout()
        self._embed_fig(fig2, self.tab2)

        # Tab 3: Centerline
        fig3, ax3 = plt.subplots(figsize=(8.5, 5))
        ax3.plot(self.sim.x / self.sim.Le, self.sim.u_centerline / self.sim.U_in, "b-", linewidth=2.2, label="Numerical uc(x)/Uin")
        ax3.axhline(y=2.0, color="r", linestyle="--", label="Asymptote (2.0)")
        ax3.axvline(x=1.0, color="g", linestyle=":", label="Entrance Length (x/Le = 1.0)")
        ax3.set_title("Centerline Velocity Evolution uc(x)/Uin", fontweight="bold")
        ax3.set_xlabel("Normalized Distance x / Le")
        ax3.set_ylabel("uc / Uin")
        ax3.grid(True, linestyle="--", alpha=0.6)
        ax3.legend()
        fig3.tight_layout()
        self._embed_fig(fig3, self.tab3)

        # Tab 4: Pressure Drop
        fig4, ax4 = plt.subplots(figsize=(8.5, 5))
        ax4.plot(self.sim.x * 1e3, (self.sim.p[0] - self.sim.p)/1e3, "purple", linewidth=2.0, label="Numerical ΔP(x)")
        ax4.plot(self.sim.x * 1e3, -self.sim.dp_dx_theoretical * self.sim.x / 1e3, "k--", label="Poiseuille Linear Slope")
        ax4.axvline(x=self.sim.Le * 1e3, color="g", linestyle=":", label="Entrance Le")
        ax4.set_title("Pressure Drop ΔP(x) along Pipe", fontweight="bold")
        ax4.set_xlabel("Axial Position x [mm]")
        ax4.set_ylabel("Pressure Drop ΔP [kPa]")
        ax4.grid(True, linestyle="--", alpha=0.6)
        ax4.legend()
        fig4.tight_layout()
        self._embed_fig(fig4, self.tab4)

    def _embed_fig(self, fig, parent_frame):
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _launch_ai_suite(self):
        import subprocess, sys, os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        ai_script = os.path.join(base_dir, "ai with pythin", "main.py")
        if os.path.exists(ai_script):
            subprocess.Popen([sys.executable, ai_script])

if __name__ == "__main__":
    root = tk.Tk()
    app = PipeFlowApp(root)
    root.mainloop()

