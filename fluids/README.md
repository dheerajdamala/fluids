# Laminar Water Flow Through a Circular Pipe (CFD Simulation) 🌊

Numerical simulation and hydrodynamic analysis of water flow through a circular pipe across three computational platforms:
1. **Python** (High-fidelity custom 2D Axisymmetric Navier-Stokes marching solver + GUI Visualizer)
2. **ANSYS Fluent** (Journal automation script `pipe_flow_fluent.jou` + PyFluent script + GUI tutorial)
3. **COMSOL Multiphysics** (MATLAB LiveLink script `pipe_flow_comsol.m` + MPh Python script + GUI tutorial)

Demonstrates the **developing (entrance) region** and **fully developed Hagen-Poiseuille flow** for an inlet velocity equal to your roll number (default: $U_{in} = 67\text{ m/s}$).

---

## 📐 Hydrodynamic Design Parameters (Roll Number: 67 Example)

| Parameter | Formula | Value | Notes |
| :--- | :--- | :---: | :--- |
| **Inlet Velocity ($U_{in}$)** | Given by roll number | **$67.0\text{ m/s}$** | Parameterized (supports any roll number) |
| **Target Reynolds Number ($Re$)** | Selected $< 2300$ | **$1600$** | Ensures strictly laminar flow |
| **Fluid** | Water at $20^\circ\text{C}$ | $\rho = 998.2\text{ kg/m}^3$ | $\mu = 1.002 \times 10^{-3}\text{ Pa}\cdot\text{s}$ |
| **Pipe Diameter ($D$)** | $D = \frac{Re \cdot \nu}{U_{in}}$ | **$23.97\ \mu\text{m}$** | Microfluidic tube diameter |
| **Pipe Radius ($R$)** | $R = D / 2$ | **$11.99\ \mu\text{m}$** | Axisymmetric domain radius |
| **Hydrodynamic Entrance ($L_e$)** | $L_e \approx 0.0575 \cdot Re \cdot D$ | **$2.21\text{ mm}$** | Length where $u_c$ reaches $99\%$ of developed state |
| **Total Pipe Length ($L$)** | $L = 1.6 \times L_e$ | **$3.53\text{ mm}$** | Captures entrance ($0 \le x \le 2.21$) + developed ($2.21 \le x \le 3.53$) |
| **Centerline Max Velocity ($u_c$)** | $u_c = 2 \times U_{in}$ | **$134.0\text{ m/s}$** | Fully developed Hagen-Poiseuille asymptote |

---

## 📁 Directory Structure

```
fluids/
├── python/
│   ├── pipe_flow_simulation.py    # 2D Axisymmetric implicit Navier-Stokes CFD solver
│   ├── visualizer.py              # Interactive Tkinter + Matplotlib GUI visualizer
│   ├── run_simulation.py          # CLI runner & publication-quality plot generator
│   └── requirements.txt           # Python dependencies (numpy, matplotlib, scipy)
├── ansys/
│   ├── pipe_flow_fluent.jou       # ANSYS Fluent automated TUI journal file
│   ├── fluent_setup_pyfluent.py   # Modern PyFluent Python automation script
│   └── ANSYS_FLUENT_GUIDE.md      # Detailed step-by-step Workbench/Fluent tutorial
├── comsol/
│   ├── pipe_flow_comsol.m         # COMSOL LiveLink for MATLAB / script model
│   ├── comsol_mph_setup.py        # Python MPh interface script
│   └── COMSOL_GUIDE.md            # Comprehensive step-by-step COMSOL modeling guide
├── results/
│   ├── velocity_contour.png       # 2D full pipe velocity colormap
│   ├── velocity_profiles.png      # Radial velocity profiles at axial stations
│   ├── centerline_velocity.png    # uc(x)/Uin development curve
│   ├── pressure_drop.png          # Pressure drop and f_app * Re convergence to 64
│   ├── wall_shear_stress.png      # Wall shear stress development
│   └── simulation_summary.csv     # Complete tabulated numerical data
├── FLUIDS_PROJECT_REPORT.md       # Full academic engineering technical report
└── README.md                      # Overview & execution instructions (this file)
```

---

## 🚀 How to Run the Simulations

### 1. Python Simulation

#### A. Run CLI Simulation & Generate High-Res Figures
```bash
cd fluids
python python/run_simulation.py --roll-number 67 --output-dir results
```
*(You can pass any roll number, e.g. `--roll-number 25`, or custom Reynolds number `--reynolds 1500`).*

#### B. Launch Interactive GUI Visualizer
```bash
cd fluids
python python/visualizer.py
```
Allows real-time parameter changes, dynamic solving, and tabbed graph browsing.

---

### 2. ANSYS Fluent Simulation

1. **Automated Journal Run (Headless / Terminal)**:
   ```bash
   fluent 2ddp -g -i ansys/pipe_flow_fluent.jou
   ```
2. **Interactive GUI Setup**:
   - Open **ANSYS Workbench**, drag **Fluid Flow (Fluent)**.
   - Follow the detailed step-by-step guide in **[ANSYS_FLUENT_GUIDE.md](file:///c:/Users/dheer/Desktop/kani/fluids/ansys/ANSYS_FLUENT_GUIDE.md)** to set up the 2D Axisymmetric domain, structured quad mesh with wall inflation, SIMPLE solver, and post-processing plots.

---

### 3. COMSOL Multiphysics Simulation

1. **Automated Script Run**:
   - In MATLAB with COMSOL LiveLink: run `ansys/pipe_flow_comsol.m`.
   - Or with Python `mph`: `python comsol/comsol_mph_setup.py 67`.
2. **Interactive GUI Setup**:
   - Open COMSOL Multiphysics $\to$ **2D Axisymmetric** $\to$ **Laminar Flow (spf)** $\to$ **Stationary**.
   - Follow the detailed walkthrough in **[COMSOL_GUIDE.md](file:///c:/Users/dheer/Desktop/kani/fluids/comsol/COMSOL_GUIDE.md)** for boundary conditions, boundary layer meshing, and 3D revolution plots.

---

## 📊 Verification & Validation

In the fully developed region ($x > 2.21\text{ mm}$):
- **Numerical Centerline Velocity**: $133.89\text{ m/s}$
- **Theoretical Hagen-Poiseuille ($2 U_{in}$)**: $134.00\text{ m/s}$
- **Agreement**: **$99.92\%$**
- **Friction Factor Product ($f \cdot Re$)**: $64.04$ (matches theoretical $64.00$).

