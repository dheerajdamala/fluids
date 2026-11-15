# Unified Computational & AI Suite ⚡

A unified desktop application integrating two major engineering modules:
1. **🤖 AI with Python**: Smart 2D Maze-Solving Robot with real-time heuristic search algorithms and directional kinematics.
2. **🌊 Fluids**: Laminar Water Flow Through a Circular Pipe (developing entrance region to fully developed Hagen-Poiseuille flow) across Python, ANSYS Fluent, and COMSOL Multiphysics.

Includes a **Main Hub / Landing Dashboard** with one-click conversion buttons enabling instantaneous switching between **AI with Python** and **Fluids**.

---

## 🚀 Quick Launch (Unified Master Application)

To launch the master unified desktop application with both modules integrated:

```bash
python app.py
```

### 🔀 Seamless Conversion & Switching:
- **From Main Hub**: Click either **`▶ LAUNCH AI MAZE SOLVER`** or **`🌊 LAUNCH FLUIDS CFD SIMULATOR`**.
- **From Anywhere**: Click the prominent top-header conversion button:
  - `🔀 SWITCH: AI with Python ➔ Fluids` (or vice versa).
- **Inside AI Module**: Dedicated button `🌊 Switch to Fluids (CFD) ➔`.
- **Inside Fluids Module**: Dedicated button `🤖 Switch to AI with Python ➔`.

---

## 📁 Repository Overview

```
kani/
├── app.py                      # Master Unified Application Launcher (Both UIs in one window)
├── README.md                   # This root documentation file
│
├── ai with pythin/             # Module 1: AI Maze-Solving Robot
│   ├── main.py                 # Standalone CLI / GUI entry point
│   ├── gui.py                  # Tkinter 2D visualizer with "Switch to Fluids" button
│   ├── robot.py                # 2D Kinematic robot entity (headlights, sensors, treads)
│   ├── algorithms.py           # BFS, DFS, UCS, A* (Manhattan & Euclidean), Greedy Best-First
│   ├── maze.py                 # Procedural maze generators (Backtracker, Prim's, Presets)
│   ├── comparison.py           # Multi-algorithm benchmark harness & Matplotlib plots
│   ├── test_algorithms.py      # Automated unit test suite (5 tests)
│   ├── PROJECT_REPORT.md       # Comprehensive academic project report (4 students)
│   └── README.md               # AI module documentation
│
├── ai with python/             # Mirrored folder with identical contents
│
└── fluids/                     # Module 2: Laminar Pipe Flow CFD Simulation
    ├── python/
    │   ├── pipe_flow_simulation.py  # 2D Axisymmetric implicit Navier-Stokes CFD solver
    │   ├── visualizer.py            # Standalone Fluids GUI with "Switch to AI" button
    │   ├── run_simulation.py        # CLI simulation runner & figure exporter
    │   └── requirements.txt         # Python dependencies
    ├── ansys/
    │   ├── pipe_flow_fluent.jou     # ANSYS Fluent automated TUI journal file
    │   ├── fluent_setup_pyfluent.py # PyFluent Python automation script
    │   └── ANSYS_FLUENT_GUIDE.md    # Step-by-step Workbench/Fluent guide
    ├── comsol/
    │   ├── pipe_flow_comsol.m       # COMSOL LiveLink for MATLAB script
    │   ├── comsol_mph_setup.py      # Python MPh interface script
    │   └── COMSOL_GUIDE.md          # Step-by-step COMSOL Multiphysics guide
    ├── results/
    │   ├── velocity_contour.png     # 2D pipe velocity colormap
    │   ├── velocity_profiles.png    # Radial profiles vs. Hagen-Poiseuille
    │   ├── centerline_velocity.png  # uc(x)/Uin development curve
    │   ├── pressure_drop.png        # Pressure drop and f_app * Re
    │   ├── wall_shear_stress.png    # Wall shear stress development
    │   └── simulation_summary.csv   # Numerical dataset
    ├── FLUIDS_PROJECT_REPORT.md     # Engineering CFD technical report
    └── README.md                    # Fluids module documentation
```

---

## 🛠 Individual Standalone Launchers

If you prefer to run either module independently:

### 1. Standalone AI Maze-Solving Robot
```bash
cd "ai with pythin"
python main.py
```
*(Includes "Switch to Fluids" button in sidebar).*

### 2. Standalone Fluids CFD Simulator
```bash
cd fluids
python python/visualizer.py
```
*(Includes "Switch to AI Maze Solver" button in header).*

