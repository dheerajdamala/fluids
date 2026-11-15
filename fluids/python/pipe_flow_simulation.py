"""
High-Fidelity 2D Axisymmetric CFD Solver for Developing Laminar Pipe Flow.
Solves the cylindrical Navier-Stokes continuity and momentum equations
from inlet (slug flow) through the hydrodynamic entrance length to fully developed
Hagen-Poiseuille flow.
"""

import numpy as np

def trapz_custom(y, x):
    """Vectorized trapezoidal integration."""
    return 0.5 * np.sum((y[:-1] + y[1:]) * np.diff(x))

class PipeFlowSimulation:
    def __init__(self, roll_number=67, target_re=1600.0, rho=998.2, mu=1.002e-3, nr=100, nx=400):
        """
        Initializes pipe flow simulation parameters based on roll number.
        
        Parameters:
        - roll_number: Last two digits of student roll number (defines U_in in m/s)
        - target_re: Reynolds number (< 2300 to ensure strictly laminar flow)
        - rho: Water density (kg/m^3) at 20 deg C
        - mu: Water dynamic viscosity (Pa.s) at 20 deg C
        - nr: Number of radial grid points
        - nx: Number of axial grid stations
        """
        self.roll_number = int(roll_number)
        self.U_in = float(self.roll_number) if self.roll_number > 0 else 10.0
        self.target_re = float(target_re)
        self.rho = float(rho)
        self.mu = float(mu)
        self.nu = self.mu / self.rho

        # Step 1: Calculate pipe diameter to guarantee laminar flow
        # Re = (U_in * D) / nu  =>  D = (Re * nu) / U_in
        self.D = (self.target_re * self.nu) / self.U_in
        self.R = self.D / 2.0
        self.Re = (self.U_in * self.D) / self.nu

        # Step 2: Calculate hydrodynamic entrance length (Le)
        # Literature standard: Le approx 0.057 * Re * D
        self.Le = 0.0575 * self.Re * self.D

        # Step 3: Total pipe length to capture both developing and fully developed regions
        self.L = 1.60 * self.Le

        # Discretization
        self.Nr = int(nr)
        self.Nx = int(nx)
        self.r = np.linspace(0.0, self.R, self.Nr)
        self.x = np.linspace(0.0, self.L, self.Nx)
        self.dr = self.r[1] - self.r[0]
        self.dx = self.x[1] - self.x[0]

        # Field arrays
        self.u = np.zeros((self.Nx, self.Nr))
        self.v = np.zeros((self.Nx, self.Nr))
        self.p = np.zeros(self.Nx)
        self.tau_w = np.zeros(self.Nx)
        self.u_centerline = np.zeros(self.Nx)
        self.f_apparent = np.zeros(self.Nx)

        # Theoretical fully developed values
        self.u_max_theoretical = 2.0 * self.U_in
        self.dp_dx_theoretical = -(32.0 * self.mu * self.U_in) / (self.D**2)
        self.tau_w_theoretical = (4.0 * self.mu * self.U_in) / self.R

    def solve(self):
        """
        Executes the implicit marching Navier-Stokes finite difference solver.
        Couples axial momentum with the global continuity constraint.
        """
        # Boundary conditions at inlet (x = 0)
        self.u[0, :] = self.U_in
        self.u[0, -1] = 0.0  # No-slip at wall
        self.v[0, :] = 0.0
        self.p[0] = 0.0
        self.u_centerline[0] = self.U_in
        self.tau_w[0] = self.mu * (self.u[0, -2] - self.u[0, -1]) / self.dr

        target_Q = np.pi * (self.R**2) * self.U_in
        dr = self.dr
        dx = self.dx
        nu = self.nu
        rho = self.rho
        Nr = self.Nr

        for i in range(self.Nx - 1):
            A = np.zeros(Nr)
            B = np.zeros(Nr)
            C = np.zeros(Nr)
            d_hom = np.zeros(Nr)
            d_part = np.zeros(Nr)

            # Centerline symmetry boundary (j = 0)
            B[0] = self.u[i, 0] / dx + 4.0 * nu / (dr**2)
            C[0] = -4.0 * nu / (dr**2)
            d_hom[0] = (self.u[i, 0]**2) / dx
            d_part[0] = 1.0

            # Interior nodes (j = 1 to Nr - 2)
            for j in range(1, Nr - 1):
                rj = self.r[j]
                uj = self.u[i, j]
                vj = self.v[i, j]
                A[j] = -vj / (2.0 * dr) - nu / (dr**2) + nu / (2.0 * rj * dr)
                B[j] = uj / dx + 2.0 * nu / (dr**2)
                C[j] = vj / (2.0 * dr) - nu / (dr**2) - nu / (2.0 * rj * dr)
                d_hom[j] = (uj**2) / dx
                d_part[j] = 1.0

            # Wall no-slip boundary (j = Nr - 1)
            B[-1] = 1.0
            d_hom[-1] = 0.0
            d_part[-1] = 0.0

            # Thomas Algorithm (TDMA) for homogeneous and particular solutions
            u_hom = self._thomas_solve(A, B, C, d_hom)
            u_part = self._thomas_solve(A, B, C, d_part)

            # Enforce global mass conservation: Q = integral(2*pi*r*u*dr) = target_Q
            integrand_hom = 2.0 * np.pi * self.r * u_hom
            integrand_part = 2.0 * np.pi * self.r * u_part
            Q_hom = trapz_custom(integrand_hom, self.r)
            Q_part = trapz_custom(integrand_part, self.r)

            # Solve for pressure gradient term P' = -(1/rho) * (dp/dx)
            P_prime = (target_Q - Q_hom) / Q_part

            # Reconstruct axial velocity at station i + 1
            self.u[i+1, :] = u_hom + P_prime * u_part
            self.u[i+1, -1] = 0.0  # Exact wall no-slip

            # Update pressure
            self.p[i+1] = self.p[i] - rho * dx * P_prime

            # Calculate radial velocity v from continuity: d(rv)/dr = -r * du/dx
            dudx = (self.u[i+1, :] - self.u[i, :]) / dx
            for j in range(1, Nr):
                integral_val = trapz_custom(self.r[:j+1] * dudx[:j+1], self.r[:j+1])
                self.v[i+1, j] = -integral_val / self.r[j]
            self.v[i+1, 0] = 0.0
            self.v[i+1, -1] = 0.0

            # Centerline velocity & wall shear stress
            self.u_centerline[i+1] = self.u[i+1, 0]
            # Second-order one-sided wall derivative for shear stress
            du_dr_wall = (3.0 * self.u[i+1, -1] - 4.0 * self.u[i+1, -2] + self.u[i+1, -3]) / (2.0 * dr)
            self.tau_w[i+1] = -self.mu * du_dr_wall

            # Apparent friction factor: f_app = (-dp/dx * D) / (0.5 * rho * U_in^2)
            if self.x[i+1] > 0:
                delta_p = self.p[0] - self.p[i+1]
                self.f_apparent[i+1] = (delta_p * self.D) / (0.5 * rho * (self.U_in**2) * self.x[i+1])

        return self

    def _thomas_solve(self, A, B, C, D):
        """Solves tridiagonal linear system A*x_{j-1} + B*x_j + C*x_{j+1} = D."""
        n = len(B)
        c_prime = np.zeros(n)
        d_prime = np.zeros(n)

        c_prime[0] = C[0] / B[0]
        d_prime[0] = D[0] / B[0]

        for k in range(1, n):
            denom = B[k] - A[k] * c_prime[k-1]
            if k < n - 1:
                c_prime[k] = C[k] / denom
            d_prime[k] = (D[k] - A[k] * d_prime[k-1]) / denom

        x = np.zeros(n)
        x[-1] = d_prime[-1]
        for k in range(n - 2, -1, -1):
            x[k] = d_prime[k] - c_prime[k] * x[k+1]

        return x

    def analytical_poiseuille_profile(self):
        """Returns the theoretical parabolic velocity profile."""
        return 2.0 * self.U_in * (1.0 - (self.r / self.R)**2)

    def summary(self):
        """Returns a formatted summary dictionary of pipe flow physics."""
        developed_idx = np.searchsorted(self.x, self.Le)
        u_developed_center = self.u_centerline[-1]
        accuracy = (u_developed_center / self.u_max_theoretical) * 100.0

        return {
            "Roll Number": self.roll_number,
            "Inlet Velocity U_in (m/s)": self.U_in,
            "Target Reynolds Number Re": self.Re,
            "Fluid": "Water at 20 deg C",
            "Density (kg/m3)": self.rho,
            "Dynamic Viscosity (Pa.s)": self.mu,
            "Pipe Diameter D (um)": self.D * 1e6,
            "Pipe Diameter D (m)": self.D,
            "Pipe Radius R (um)": self.R * 1e6,
            "Entrance Length Le (mm)": self.Le * 1e3,
            "Total Pipe Length L (mm)": self.L * 1e3,
            "L / Le Ratio": self.L / self.Le,
            "Outlet Centerline Velocity (m/s)": u_developed_center,
            "Theoretical Fully Developed u_max (m/s)": self.u_max_theoretical,
            "Centerline Velocity Accuracy (%)": accuracy,
            "Theoretical Pressure Gradient (MPa/m)": self.dp_dx_theoretical / 1e6,
            "Theoretical Wall Shear Stress (kPa)": self.tau_w_theoretical / 1e3
        }

