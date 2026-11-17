# Laminar Water Pipe Flow CFD Simulation

Numerical simulation of water flow through a circular pipe from a uniform slug inlet across the hydrodynamic entrance length to fully developed Hagen-Poiseuille parabolic laminar flow, using Python, ANSYS Fluent, and COMSOL Multiphysics.

**Live Web Application**: [https://fluids-pipe-cfd.netlify.app](https://fluids-pipe-cfd.netlify.app)

---

## 1. Problem Specification

* **Working Fluid**: Pure liquid water ($\rho = 998.2\text{ kg/m}^3$, $\mu = 1.003 \times 10^{-3}\text{ Pa}\cdot\text{s}$, $\nu = 1.0048 \times 10^{-6}\text{ m}^2/\text{s}$).
* **Inlet Velocity**: $U_{in} = 67\text{ m/s}$ (Parameterized by student roll number ending in $67$).
* **Flow Regime**: Strictly laminar flow requiring $Re = \frac{\rho U_{in} D}{\mu} < 2300$.
* **Target Reynolds Number**: $Re = 1600$ (safely below the critical transition threshold of $2300$).
* **Pipe Diameter Calculation**:
  $$D = \frac{Re \cdot \mu}{\rho \cdot U_{in}} = \frac{1600 \cdot 1.003 \times 10^{-3}}{998.2 \cdot 67} \approx 2.397 \times 10^{-5}\text{ m} = 23.97\text{ }\mu\text{m}$$
  $$\text{Pipe Radius } R = \frac{D}{2} \approx 11.986\text{ }\mu\text{m}$$
* **Hydrodynamic Entrance Length**:
  $$L_e \approx 0.06 \cdot Re \cdot D = 0.06 \cdot 1600 \cdot 2.397 \times 10^{-5}\text{ m} \approx 2.301\text{ mm}$$
* **Total Pipe Length**:
  $$L = 1.6 \cdot L_e \approx 3.682\text{ mm}$$
  Ensures both developing entrance region ($0 \le x \le L_e$) and fully developed Hagen-Poiseuille flow ($L_e \le x \le L$) are captured.

---

## 2. Governing Equations

The flow is governed by the 2D axisymmetric incompressible steady Navier-Stokes and continuity equations:

$$\frac{\partial u}{\partial x} + \frac{1}{r} \frac{\partial (r v)}{\partial r} = 0$$

$$u \frac{\partial u}{\partial x} + v \frac{\partial u}{\partial r} = -\frac{1}{\rho}\frac{dP}{dx} + \nu \left( \frac{\partial^2 u}{\partial r^2} + \frac{1}{r}\frac{\partial u}{\partial r} \right)$$

### Boundary Conditions
1. **Pipe Inlet ($x = 0$)**: Uniform slug flow $u(0, r) = U_{in} = 67\text{ m/s}$, $v(0, r) = 0$, $P(0) = P_{in}$.
2. **Pipe Wall ($r = R$)**: No-slip and impermeability $u(x, R) = 0$, $v(x, R) = 0$.
3. **Pipe Centerline ($r = 0$)**: Axisymmetry $\left.\frac{\partial u}{\partial r}\right|_{r=0} = 0$, $v(x, 0) = 0$.
4. **Fully Developed Asymptote ($x \ge L_e$)**: Hagen-Poiseuille parabolic profile:
   $$u(r) = 2 U_{in} \left[ 1 - \left(\frac{r}{R}\right)^2 \right]$$
   Peak centerline velocity: $u_c = 2 \cdot U_{in} = 134\text{ m/s}$.

---

## 3. Multi-Tool Simulation Implementations

1. **Python Numerical Solver (`fluids/python/`)**:
   - 2D axisymmetric finite difference boundary layer solver on non-uniform staggered grid ($N_r = 80$, $N_x = 300$).
   - Real-time continuity mass conservation and tridiagonal matrix algorithm (TDMA).
2. **ANSYS Fluent (`fluids/ansys/`)**:
   - Automated journal file `pipe_laminar_journal.jou` setting up 2D axisymmetric domain, inflation layers at the wall, and second-order upwind spatial discretization.
3. **COMSOL Multiphysics (`fluids/comsol/`)**:
   - Java/M-file model script `pipe_flow_model.java` utilizing the Laminar Flow (spf) physics interface with mapped boundary quadrilateral mesh.
4. **Interactive Web Application**:
   - Pure client-side HTML5/Canvas & Chart.js simulation suite with real-time 2D velocity colormap and radial profile extraction.

---

## 4. Repository Structure

```
fluids/
├── index.html            # Standalone web CFD visualizer
├── css/
│   └── style.css         # UI stylesheet
├── js/
│   ├── fluids_cfd.js     # 2D axisymmetric Navier-Stokes solver
│   └── app.js            # UI controller & Chart.js plots
├── fluids/               # Simulation code across tools
│   ├── python/           # Python solver & visualizer
│   ├── ansys/            # ANSYS Fluent journal & geometry
│   └── comsol/           # COMSOL Multiphysics model script
├── netlify.toml          # Netlify configuration
└── render.yaml           # Render deployment specification
```

---

## 5. How to Run

### Web Application
Open `index.html` in any browser, or visit [https://fluids-pipe-cfd.netlify.app](https://fluids-pipe-cfd.netlify.app).

### Python Solver
```bash
cd fluids/python
pip install -r requirements.txt
python solver.py
python visualizer.py
```
