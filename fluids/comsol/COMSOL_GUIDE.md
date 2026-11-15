# COMSOL Multiphysics Step-by-Step Simulation Guide: Laminar Pipe Flow

This guide walks you through setting up and running the developing and fully developed laminar pipe flow simulation in **COMSOL Multiphysics** (Version 5.5 / 5.6 / 6.0 / 6.1 / 6.2) using the **2D Axisymmetric Laminar Flow** interface.

---

## 1. Parameters Definition (Roll No: 67 Example)

Open COMSOL Multiphysics $\to$ **New** $\to$ **Model Wizard**.

In **Global Definitions** $\to$ **Parameters 1**, enter the following expressions:

| Name | Expression | Value | Description |
| :--- | :--- | :--- | :--- |
| `U_in` | `67[m/s]` | $67\text{ m/s}$ | Inlet velocity (from roll number) |
| `Re_target` | `1600` | $1600$ | Target Reynolds number ($< 2300$ for laminar) |
| `rho_w` | `998.2[kg/m^3]` | $998.2\text{ kg/m}^3$ | Water density at $20^\circ\text{C}$ |
| `mu_w` | `1.002e-3[Pa*s]` | $1.002\times 10^{-3}\text{ Pa}\cdot\text{s}$ | Dynamic viscosity of water |
| `nu_w` | `mu_w/rho_w` | $1.0038\times 10^{-6}\text{ m}^2/\text{s}$ | Kinematic viscosity |
| `D` | `Re_target*nu_w/U_in` | $23.97\ \mu\text{m}$ | Laminar pipe diameter |
| `R` | `D/2` | $11.99\ \mu\text{m}$ | Pipe radius |
| `Le` | `0.0575*Re_target*D` | $2.21\text{ mm}$ | Hydrodynamic entrance length |
| `L` | `1.6*Le` | $3.53\text{ mm}$ | Total pipe length (developing + developed) |

---

## 2. Model Wizard Setup

1. **Select Space Dimension**: Choose **2D Axisymmetric** (coordinates: $r, z$).
   - The $r$-axis represents the radial direction from centerline to wall ($r \ge 0$).
   - The $z$-axis represents the axial flow direction along the pipe ($0 \le z \le L$).
2. **Select Physics**: Expand **Fluid Flow** $\to$ **Single-Phase Flow** $\to$ select **Laminar Flow (spf)** $\to$ click **Add**.
3. **Select Study**: Choose **Stationary** $\to$ click **Done**.

---

## 3. Geometry Construction

1. In Model Builder, right-click **Component 1** $\to$ **Geometry 1** $\to$ set Length unit to **mm** (or $\mu\text{m}$).
2. Right-click **Geometry 1** $\to$ **Rectangle** (`r1`):
   - Position: $r = 0$, $z = 0$.
   - Width ($r$-direction): `R`
   - Height ($z$-direction): `L`
3. Click **Build All Objects**.
   - You will see a tall, narrow rectangular domain with the left edge lying on the symmetry axis $r = 0$.

---

## 4. Materials Setup

1. Right-click **Component 1** $\to$ **Materials** $\to$ **Add Material from Library**.
2. Expand **Built-in** $\to$ select **Water, liquid** $\to$ click **Add to Component 1**.
3. Ensure the rectangular domain is assigned to `Water, liquid`.
   - Properties $\rho = \text{rho\_w}$ and $\mu = \text{mu\_w}$ are automatically mapped to the Navier-Stokes equations.

---

## 5. Physics: Laminar Flow (`spf`) Boundary Conditions

1. **Axial Symmetry 1**:
   - Boundary 1 ($r = 0$) is automatically recognized as the symmetry axis $\partial u_z / \partial r = 0, u_r = 0$.
2. **Inlet 1**:
   - Right-click **Laminar Flow (spf)** $\to$ **Inlet**.
   - Select Boundary 2 (bottom edge: $z = 0$).
   - Boundary condition: **Velocity** $\to$ Normal inflow velocity: `U_in` ($67\text{ m/s}$).
3. **Outlet 1**:
   - Right-click **Laminar Flow (spf)** $\to$ **Outlet**.
   - Select Boundary 3 (top edge: $z = L$).
   - Boundary condition: **Pressure** $\to$ Static pressure $p_0 = 0\text{ Pa}$.
4. **Wall 1**:
   - Boundary 4 (outer edge at $r = R$) is assigned the default **Wall (No slip)** condition: $\mathbf{u} = \mathbf{0}$.

---

## 6. Meshing (Boundary Layer Resolution)

1. In Model Builder, click **Mesh 1**.
2. Sequence type: **User-controlled mesh**.
3. Right-click **Mesh 1** $\to$ **Free Quad**.
4. Right-click **Mesh 1** $\to$ **Boundary Layers**:
   - Boundary Selection: Select Boundary 4 (outer pipe wall at $r = R$).
   - Number of boundary layers: `8`.
   - Boundary layer stretching factor: `1.2`.
5. Under **Size**: Element size: **Extra fine**.
6. Click **Build All**.

---

## 7. Study Execution

1. In Model Builder, click **Study 1**.
2. Click **Compute** (= button) on the ribbon.
3. The PARDISO / MUMPS direct sparse linear solver will solve the coupled continuity and momentum equations in 10–25 seconds.

---

## 8. Results & Plots

### A. 2D Revolution Surface (3D Cylindrical Pipe View)
1. Right-click **Datasets** $\to$ **Revolution 2D** (revolves 2D axisymmetric solution around the $z$-axis to form a full 3D cylinder).
2. Right-click **Results** $\to$ **3D Plot Group** $\to$ **Surface** $\to$ Expression: `spf.U` (Velocity magnitude).
3. Result: Displays the 3D velocity core inside the pipe with the developing shear layer.

### B. Centerline Velocity Evolution ($u_z(0, z)$)
1. Right-click **Results** $\to$ **1D Plot Group** $\to$ rename to `Centerline Velocity`.
2. Right-click $\to$ **Line Graph** $\to$ Selection: Boundary 1 ($r = 0$).
3. Expression: `w` (or `spf.uz`) $\to$ Unit: `m/s`.
4. Click **Plot**:
   - At $z = 0$: $u_z = 67\text{ m/s}$.
   - Over $0 \le z \le 2.21\text{ mm}$: $u_z$ accelerates asymptotically to $133.9\text{ m/s}$ ($2 \times U_{in}$).
   - Over $2.21\text{ mm} \le z \le 3.53\text{ mm}$: $u_z$ remains constant at $134.0\text{ m/s}$.

### C. Radial Velocity Profiles at Axial Stations
1. Right-click **Datasets** $\to$ **Cut Line 2D** (define horizontal lines across $r$ at $z = 0.1\text{ mm}, 0.5\text{ mm}, 1.5\text{ mm}, 2.5\text{ mm}$).
2. Right-click **Results** $\to$ **1D Plot Group** $\to$ **Line Graph** using the Cut Line datasets.
3. Plot shows the transition from flat inlet slug flow to the parabolic Hagen-Poiseuille curve.

