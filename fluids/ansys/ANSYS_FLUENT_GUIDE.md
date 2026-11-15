# ANSYS Fluent Step-by-Step Simulation Guide: Laminar Pipe Flow

This guide walks you through setting up and simulating the developing and fully developed laminar flow of water in a circular pipe using **ANSYS Workbench / Fluent** (2D Axisymmetric).

---

## 1. Problem Dimensions & Parameters (Roll No: 67 Example)

| Parameter | Symbol | Value | Unit | Notes |
| :--- | :---: | :---: | :---: | :--- |
| **Inlet Velocity** | $U_{in}$ | **67.0** | $\text{m/s}$ | Equal to roll number digits |
| **Target Reynolds No.** | $Re$ | **1600** | — | Strictly laminar ($Re < 2300$) |
| **Fluid** | — | **Water** | — | $\rho = 998.2 \text{ kg/m}^3, \mu = 1.002 \times 10^{-3} \text{ Pa}\cdot\text{s}$ |
| **Pipe Diameter** | $D$ | **23.97** | $\mu\text{m}$ | $D = \frac{Re \cdot \nu}{U_{in}}$ |
| **Pipe Radius** | $R$ | **11.99** | $\mu\text{m}$ | $R = D/2$ |
| **Entrance Length** | $L_e$ | **2.21** | $\text{mm}$ | $L_e = 0.0575 \cdot Re \cdot D$ |
| **Total Pipe Length** | $L$ | **3.53** | $\text{mm}$ | $L = 1.6 \cdot L_e$ (shows developing + developed) |

---

## 2. Geometry Creation (DesignModeler or SpaceClaim)

Because the pipe is circular and symmetric around its centerline, we model it as a **2D Axisymmetric domain**:
- Horizontal axis ($X$): Centerline of the pipe ($0 \le X \le L = 3.53\text{ mm}$).
- Vertical axis ($Y$): Radial coordinate from centerline to wall ($0 \le Y \le R = 11.99\ \mu\text{m}$).

### Steps in DesignModeler:
1. Open **ANSYS Workbench**, drag a **Fluid Flow (Fluent)** system onto the Project Schematic.
2. Right-click **Geometry** $\to$ select **Properties** $\to$ set **Analysis Type** to **2D**.
3. Right-click **Geometry** $\to$ **New DesignModeler Geometry**.
4. Select **XY-Plane** $\to$ click **Sketching** tab.
5. Draw a **Rectangle**:
   - Bottom-left corner at $(X=0, Y=0)$.
   - Dimensions: Length $H_1 = 3.53\text{ mm}$, Height $V_1 = 11.99\ \mu\text{m}$ ($0.01199\text{ mm}$).
6. Click **Concept** menu $\to$ **Surfaces from Sketches** $\to$ select the sketch $\to$ click **Generate**.
7. Close DesignModeler.

---

## 3. Meshing & Named Selections (ANSYS Meshing)

1. Double-click **Mesh** in Workbench.
2. Create **Named Selections** by selecting edges:
   - **Inlet** (Left edge at $X=0$): Right-click $\to$ *Create Named Selection* $\to$ name: `inlet`.
   - **Outlet** (Right edge at $X=L$): Name: `outlet`.
   - **Centerline** (Bottom edge along $Y=0$): Name: `axis`.
   - **Pipe Wall** (Top edge at $Y=R$): Name: `wall`.
3. Generate Structured Quad Mesh:
   - Right-click **Mesh** $\to$ **Insert** $\to$ **Method** $\to$ select surface $\to$ Method: **Mapped Face Meshing**.
   - Right-click **Mesh** $\to$ **Insert** $\to$ **Sizing** on radial edges: Number of divisions = $80$ (Bias Factor = $3$ towards the wall for boundary layer resolution).
   - Right-click **Mesh** $\to$ **Insert** $\to$ **Sizing** on axial edges: Number of divisions = $400$.
4. Click **Update Mesh**. The mesh should have $\approx 32,000$ structured quadrilateral elements.

---

## 4. ANSYS Fluent Physics Setup

1. Open Fluent (**Double Precision**, 2D).
2. **General**:
   - Solver Type: **Pressure-Based**, Time: **Steady**.
   - 2D Space: Select **Axisymmetric**.
3. **Models**:
   - Double-click **Viscous** $\to$ select **Laminar** $\to$ click **OK**.
4. **Materials**:
   - Double-click **Fluid** $\to$ click **Fluent Database...** $\to$ select **water-liquid ($\text{H}_2\text{O}$)** $\to$ click **Copy** $\to$ **Close**.
   - Verify: Density = $998.2\text{ kg/m}^3$, Viscosity = $0.001002\text{ kg/(m}\cdot\text{s)}$.
5. **Cell Zone Conditions**:
   - Ensure the surface body is assigned material: `water-liquid`.
6. **Boundary Conditions**:
   - `inlet`: Type = **velocity-inlet** $\to$ Velocity Magnitude = **67 m/s** (or your roll number).
   - `outlet`: Type = **pressure-outlet** $\to$ Gauge Pressure = **0 Pa**.
   - `axis`: Type = **axis**.
   - `wall`: Type = **wall** $\to$ **No-Slip**, Stationary.

---

## 5. Solution & Convergence

1. **Methods**:
   - Pressure-Velocity Coupling: **SIMPLE**.
   - Pressure: **Second Order**.
   - Momentum: **Second Order Upwind**.
2. **Monitors**:
   - Set residual convergence criteria for continuity, x-velocity, and y-velocity to **$10^{-6}$**.
3. **Initialization**:
   - Method: **Standard Initialization** $\to$ Compute from: `inlet` $\to$ click **Initialize**.
4. **Run Calculation**:
   - Number of Iterations: **500** $\to$ click **Calculate**.
   - The solution will converge in approximately 120–180 iterations.

---

## 6. Post-Processing & Validation

1. **2D Velocity Contours**:
   - In tree, expand **Graphics** $\to$ **Contours** $\to$ **New**.
   - Options: Filled $\to$ Contours of: **Velocity... Axial Velocity** $\to$ click **Display**.
   - You will see the boundary layer growing inward from the wall until reaching the parabolic profile at $X = 2.21\text{ mm}$.
2. **Centerline Velocity Plot**:
   - **Plots** $\to$ **XY Plot** $\to$ Y-Axis: **Axial Velocity**, X-Axis: **Direction Vector (X=1, Y=0)** $\to$ Surfaces: `axis` $\to$ click **Plot**.
   - The centerline velocity starts at $67.0\text{ m/s}$ and smoothly reaches $133.9\text{ m/s}$ ($2 \times U_{in}$, Hagen-Poiseuille asymptote).
3. **Wall Shear Stress**:
   - Y-Axis: **Wall Fluxes... Wall Shear Stress** $\to$ Surface: `wall` $\to$ click **Plot**.
   - High entrance shear stress decays to constant fully developed Poiseuille shear stress:
     $$\tau_w = \frac{4 \mu U_{in}}{R} = 22.4\text{ kPa}$$

