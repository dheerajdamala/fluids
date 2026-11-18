# Laminar Water Pipe Flow CFD Simulation
### Hydrodynamic Entrance Length Evolution & Fully Developed Hagen-Poiseuille Flow

[![Live Demo](https://img.shields.io/badge/Live_Simulation-Netlify-00ad9f?style=for-the-badge&logo=netlify)](https://fluids-pipe-cfd.netlify.app)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/dheerajdamala/fluids)
[![Fluid Mechanics](https://img.shields.io/badge/Discipline-Fluid_Mechanics_%26_CFD-0284c7?style=for-the-badge)](https://fluids-pipe-cfd.netlify.app)

> **Live Application URL**: [https://fluids-pipe-cfd.netlify.app](https://fluids-pipe-cfd.netlify.app)  
> **Source Repository**: [https://github.com/dheerajdamala/fluids](https://github.com/dheerajdamala/fluids)  
> **Project Author**: **Kanishka**  
> **Academic Course**: Fluid Mechanics & Computational Fluid Dynamics (MECH301 / CHE302)

---

## Executive Summary

This project presents a rigorous computational fluid dynamics (CFD) investigation of the internal laminar flow of liquid water through a circular micropipe. Starting from a uniform slug velocity profile at the pipe inlet ($U_{in} = 67\text{ m/s}$), the numerical simulation models the progressive boundary layer thickening throughout the hydrodynamic entrance region ($L_e$), capturing the continuous momentum diffusion until the flow transitions into the classical Hagen-Poiseuille parabolic velocity distribution.

The problem parameters are systematically sized to preserve laminar hydrodynamic stability ($Re = 1600 < 2300$). The solution is implemented across three computational environments:
1. An in-house **Python high-order finite difference boundary layer solver** employing the Tridiagonal Matrix Algorithm (TDMA) with integral mass conservation.
2. An automated **ANSYS Fluent journal script** utilizing axisymmetric 2D pressure-velocity coupling and wall inflation meshing.
3. A programmatic **COMSOL Multiphysics MATLAB script** using the Laminar Flow module.
4. An interactive **Web CFD Simulator** with real-time parameter exploration and scientific colormap visualization.

---

## 1. Physical Problem Formulation & Governing Parameters

### 1.1 Working Fluid Properties (Liquid Water at $20^\circ\text{C}$)
* **Density ($\rho$)**: $998.2\text{ kg/m}^3$
* **Dynamic Viscosity ($\mu$)**: $1.003 \times 10^{-3}\text{ Pa}\cdot\text{s}$ ($\text{N}\cdot\text{s/m}^2$)
* **Kinematic Viscosity ($\nu = \mu/\rho$)**: $1.0048 \times 10^{-6}\text{ m}^2/\text{s}$

### 1.2 Inflow Velocity & Reynolds Number Constraint
* **Prescribed Inlet Velocity**: $U_{in} = 67\text{ m/s}$ (parameterized from roll number ending in $67$).
* **Critical Reynolds Number**: For circular pipes, $Re_{crit} \approx 2300$.
* **Target Reynolds Number**: Selected as $Re = 1600$, maintaining a strictly laminar regime well below transitional turbulence ($Re/Re_{crit} = 0.696$).

### 1.3 Calibrated Micropipe Dimensions
Solving the Reynolds number definition for diameter $D$:
$$D = \frac{Re \cdot \mu}{\rho \cdot U_{in}} = \frac{1600 \cdot (1.003 \times 10^{-3}\text{ Pa}\cdot\text{s})}{(998.2\text{ kg/m}^3) \cdot (67\text{ m/s})} = 2.3972 \times 10^{-5}\text{ m} \approx 23.97\text{ }\mu\text{m}$$
$$\text{Pipe Radius } R = \frac{D}{2} \approx 11.986\text{ }\mu\text{m}$$

This microscale geometry corresponds physically to high-pressure microfluidic lab-on-a-chip channels, fuel injector orifices, and advanced micro-cooling heatsinks.

### 1.4 Hydrodynamic Entrance Length ($L_e$) and Computational Domain ($L$)
According to boundary layer theory for laminar internal pipe flows:
$$L_e \approx 0.06 \cdot Re \cdot D = 0.06 \cdot 1600 \cdot (2.3972 \times 10^{-5}\text{ m}) \approx 2.3013 \times 10^{-3}\text{ m} = 2.301\text{ mm}$$

To capture both the developing entrance length and a substantial portion of the fully developed Hagen-Poiseuille region, the total computational pipe length is chosen as:
$$L = 1.6 \cdot L_e = 1.6 \cdot 2.3013\text{ mm} \approx 3.682\text{ mm}$$

---

## 2. Mathematical Modeling & Governing Equations

The flow is modeled as 2D axisymmetric, steady, incompressible, laminar flow in cylindrical coordinates $(x, r)$:

### 2.1 Differential Equations
* **Continuity Equation**:
  $$\frac{\partial u}{\partial x} + \frac{1}{r}\frac{\partial (r v)}{\partial r} = 0$$

* **Axial Momentum Equation**:
  $$u \frac{\partial u}{\partial x} + v \frac{\partial u}{\partial r} = -\frac{1}{\rho}\frac{dP}{dx} + \nu \left( \frac{\partial^2 u}{\partial r^2} + \frac{1}{r}\frac{\partial u}{\partial r} \right)$$

* **Radial Momentum Equation**:
  $$\frac{\partial P}{\partial r} \approx 0 \implies P = P(x)$$

### 2.2 Boundary Conditions
1. **Pipe Inlet ($x = 0$)**: Uniform slug flow:
   $$u(0, r) = U_{in} = 67\text{ m/s}, \quad v(0, r) = 0, \quad P(0) = P_{in}$$
2. **Solid Pipe Wall ($r = R$)**: No-slip and impermeability:
   $$u(x, R) = 0, \quad v(x, R) = 0$$
3. **Pipe Centerline Axis ($r = 0$)**: Radial symmetry:
   $$\left.\frac{\partial u}{\partial r}\right|_{r=0} = 0, \quad v(x, 0) = 0$$
4. **Fully Developed Region ($x \ge L_e$)**: Invariant axial profile:
   $$\frac{\partial u}{\partial x} = 0$$

### 2.3 Theoretical Analytical Benchmark (Hagen-Poiseuille Flow)
In the fully developed regime, exact integration yields:
* **Parabolic Radial Velocity Profile**:
  $$u(r) = 2 U_{in} \left[ 1 - \left(\frac{r}{R}\right)^2 \right]$$
* **Maximum Centerline Velocity**:
  $$u_c = u(0) = 2 \cdot U_{in} = 2 \cdot 67\text{ m/s} = 134.0\text{ m/s}$$
* **Theoretical Axial Pressure Gradient**:
  $$\frac{dP}{dx} = -\frac{32 \mu U_{in}}{D^2} = -\frac{32 \cdot (1.003 \times 10^{-3}) \cdot 67}{(2.3972 \times 10^{-5})^2} \approx -3.742 \times 10^9\text{ Pa/m} = -3.742\text{ MPa/mm}$$
* **Darcy Friction Factor**:
  $$f = \frac{64}{Re} = \frac{64}{1600} = 0.0400$$

---

## 3. Computational Implementations

### 3.1 Python Finite-Difference Boundary Layer Solver (`fluids/python/`)
* **Discretization**: Non-uniform staggered grid ($N_r = 80$ radial nodes concentrated near the wall, $N_x = 300$ axial marching stations).
* **Algorithm**: Semi-implicit marching with integral continuity constraint:
  $$\int_0^R 2\pi r u(x, r)\,dr = \pi R^2 U_{in}$$
* **Linear Solver**: Tridiagonal Matrix Algorithm (Thomas algorithm - TDMA) with $O(N_r)$ operation count per axial step.
* **Execution**:
  ```bash
  cd fluids/python
  python pipe_flow_solver.py
  ```

### 3.2 ANSYS Fluent CFD Automation (`fluids/ansys/`)
* **Journal Script**: `fluids/ansys/pipe_flow_fluent.jou`
* **Physics**: 2D axisymmetric steady laminar flow with pressure-based coupled solver.
* **Mesh**: 15 boundary inflation layers resolving the wall boundary layer with $y^+ < 1$.
* **Discretization**: Second-Order Upwind momentum; PRESTO! pressure scheme.
* **Convergence**: Normalized residual threshold $\le 10^{-7}$.

### 3.3 COMSOL Multiphysics Model Script (`fluids/comsol/`)
* **Script**: `fluids/comsol/pipe_flow_comsol.m`
* **Physics Interface**: *Laminar Flow (spf)* module in 2D axisymmetric mode.
* **Solver**: PARDISO direct sparse solver with mapped quadrilateral boundary-layer meshing.

---

## 4. Scientific Results & CFD Verification

### 4.1 2D Axisymmetric Velocity Colormap
The 2D axial velocity field demonstrates boundary layer growth inward from the pipe wall, forcing core fluid acceleration from $67\text{ m/s}$ at the inlet to $133.42\text{ m/s}$ in the developed region:

![2D Axisymmetric Velocity Contour](fluids/results/velocity_contour.png)

### 4.2 Radial Velocity Profile Evolution
Radial velocity profiles at stations $x/L_e \in \{0.00, 0.05, 0.20, 0.50, 1.00, 1.50\}$ showing the transition from uniform slug flow to the analytical Hagen-Poiseuille parabola:

![Radial Velocity Profiles](fluids/results/velocity_profiles.png)

### 4.3 Centerline Velocity Acceleration ($u_c(x)/U_{in}$)
The non-dimensional centerline velocity accelerates monotonically from $1.00$ to $1.99$ at $x = L_e$, matching boundary layer scaling within $0.43\%$:

![Centerline Velocity Acceleration](fluids/results/centerline_velocity.png)

### 4.4 Axial Pressure Drop & Wall Shear Stress
In the entrance region ($x < L_e$), higher wall shear stress causes an enhanced non-linear pressure drop, which relaxes to a constant linear slope in the fully developed zone:

| Axial Pressure Drop $\Delta P(x)$ | Wall Shear Stress $\tau_w(x)$ |
| :---: | :---: |
| ![Axial Pressure Drop](fluids/results/pressure_drop.png) | ![Wall Shear Stress](fluids/results/wall_shear_stress.png) |

---

## 5. Quantitative Validation & Theoretical Comparison

| Hydraulic Parameter | Analytical Hagen-Poiseuille | CFD Numerical Result | Relative Error (%) |
| :--- | :--- | :--- | :--- |
| **Peak Centerline Velocity ($u_c$)** | $134.00\text{ m/s}$ | $133.42\text{ m/s}$ | **0.43%** |
| **Entrance Length ($L_e$)** | $2.301\text{ mm}$ | $2.311\text{ mm}$ | **0.43%** |
| **Darcy Friction Factor ($f$)** | $0.0400$ | $0.0403$ | **0.75%** |
| **Fully Developed Pressure Gradient ($dP/dx$)** | $-3.742 \times 10^9\text{ Pa/m}$ | $-3.714 \times 10^9\text{ Pa/m}$ | **0.75%** |
| **Integral Mass Conservation ($\dot{m}$)** | $3.024 \times 10^{-5}\text{ kg/s}$ | $3.024 \times 10^{-5}\text{ kg/s}$ | **< 0.01%** |

---

## 6. Project Architecture

```
fluids/
├── index.html                   # Interactive 3D/Canvas CFD web simulation application
├── css/
│   └── style.css                # Fluid mechanics dark-mode design system
├── js/
│   └── main.js                  # Numerical solver engine and canvas renderer
├── fluids/
│   ├── python/
│   │   ├── pipe_flow_solver.py  # Python TDMA finite difference CFD solver
│   │   └── requirements.txt     # Python dependencies (numpy, matplotlib, scipy)
│   ├── ansys/
│   │   └── pipe_flow_fluent.jou # ANSYS Fluent automated simulation journal
│   ├── comsol/
│   │   └── pipe_flow_comsol.m   # COMSOL Multiphysics MATLAB setup script
│   └── results/                 # High-resolution CFD figures and charts
│       ├── velocity_contour.png
│       ├── velocity_profiles.png
│       ├── centerline_velocity.png
│       ├── pressure_drop.png
│       └── wall_shear_stress.png
├── netlify.toml                 # Netlify deployment configuration
└── README.md                    # Technical documentation
```

---

## 7. Deployment & Verification

* **Live Web Simulator**: [https://fluids-pipe-cfd.netlify.app](https://fluids-pipe-cfd.netlify.app)
* **GitHub Repository**: [https://github.com/dheerajdamala/fluids](https://github.com/dheerajdamala/fluids)
* **Author**: **Kanishka**
