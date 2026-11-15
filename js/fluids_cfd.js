/**
 * 2D Axisymmetric Incompressible Navier-Stokes CFD Solver (JavaScript)
 * Solves developing laminar pipe flow from uniform slug inlet to fully developed
 * Hagen-Poiseuille flow using an implicit marching finite-difference scheme.
 */

class PipeFlowCFD {
  constructor(rollNumber = 67, targetRe = 1600, nr = 80, nx = 300) {
    this.rollNumber = parseInt(rollNumber) || 67;
    this.U_in = this.rollNumber > 0 ? this.rollNumber : 10.0;
    this.targetRe = parseFloat(targetRe) || 1600.0;
    this.rho = 998.2;       // Water density kg/m^3 at 20C
    this.mu = 1.002e-3;     // Water dynamic viscosity Pa.s
    this.nu = this.mu / this.rho;

    // Fluid mechanics parameter derivations
    this.D = (this.targetRe * this.nu) / this.U_in;
    this.R = this.D / 2.0;
    this.Re = (this.U_in * this.D) / this.nu;
    this.Le = 0.0575 * this.Re * this.D;
    this.L = 1.60 * this.Le;

    // Discretization
    this.Nr = parseInt(nr) || 80;
    this.Nx = parseInt(nx) || 300;
    this.dr = this.R / (this.Nr - 1);
    this.dx = this.L / (this.Nx - 1);

    this.r = Array.from({ length: this.Nr }, (_, j) => j * this.dr);
    this.x = Array.from({ length: this.Nx }, (_, i) => i * this.dx);

    // Fields
    this.u = Array.from({ length: this.Nx }, () => new Float64Array(this.Nr));
    this.v = Array.from({ length: this.Nx }, () => new Float64Array(this.Nr));
    this.p = new Float64Array(this.Nx);
    this.tau_w = new Float64Array(this.Nx);
    this.u_centerline = new Float64Array(this.Nx);
    this.f_apparent = new Float64Array(this.Nx);

    // Exact theoretical values
    this.u_max_theoretical = 2.0 * this.U_in;
    this.dp_dx_theoretical = -(32.0 * this.mu * this.U_in) / (this.D * this.D);
    this.tau_w_theoretical = (4.0 * this.mu * this.U_in) / this.R;
  }

  solve() {
    const Nr = this.Nr;
    const Nx = this.Nx;
    const dr = this.dr;
    const dx = this.dx;
    const nu = this.nu;
    const rho = this.rho;
    const targetQ = Math.PI * (this.R * this.R) * this.U_in;

    // Inlet Condition (x = 0)
    for (let j = 0; j < Nr - 1; j++) this.u[0][j] = this.U_in;
    this.u[0][Nr - 1] = 0.0; // Wall no-slip
    this.u_centerline[0] = this.U_in;
    this.tau_w[0] = this.mu * (this.u[0][Nr - 2] - this.u[0][Nr - 1]) / dr;

    const A = new Float64Array(Nr);
    const B = new Float64Array(Nr);
    const C = new Float64Array(Nr);
    const dHom = new Float64Array(Nr);
    const dPart = new Float64Array(Nr);

    // Implicit Marching Loop
    for (let i = 0; i < Nx - 1; i++) {
      // Centerline boundary (j = 0)
      B[0] = this.u[i][0] / dx + (4.0 * nu) / (dr * dr);
      C[0] = -(4.0 * nu) / (dr * dr);
      dHom[0] = (this.u[i][0] * this.u[i][0]) / dx;
      dPart[0] = 1.0;

      // Interior nodes (j = 1 .. Nr - 2)
      for (let j = 1; j < Nr - 1; j++) {
        const rj = this.r[j];
        const uj = this.u[i][j];
        const vj = this.v[i][j];

        A[j] = -vj / (2.0 * dr) - nu / (dr * dr) + nu / (2.0 * rj * dr);
        B[j] = uj / dx + (2.0 * nu) / (dr * dr);
        C[j] = vj / (2.0 * dr) - nu / (dr * dr) - nu / (2.0 * rj * dr);
        dHom[j] = (uj * uj) / dx;
        dPart[j] = 1.0;
      }

      // Wall boundary (j = Nr - 1)
      B[Nr - 1] = 1.0;
      dHom[Nr - 1] = 0.0;
      dPart[Nr - 1] = 0.0;

      // Thomas Algorithm for homogeneous and particular components
      const uHom = this.thomasSolve(A, B, C, dHom);
      const uPart = this.thomasSolve(A, B, C, dPart);

      // Trapezoidal integration for global continuity
      let QHom = 0.0;
      let QPart = 0.0;
      for (let j = 0; j < Nr - 1; j++) {
        const fH1 = 2.0 * Math.PI * this.r[j] * uHom[j];
        const fH2 = 2.0 * Math.PI * this.r[j + 1] * uHom[j + 1];
        QHom += 0.5 * (fH1 + fH2) * dr;

        const fP1 = 2.0 * Math.PI * this.r[j] * uPart[j];
        const fP2 = 2.0 * Math.PI * this.r[j + 1] * uPart[j + 1];
        QPart += 0.5 * (fP1 + fP2) * dr;
      }

      // Exact pressure gradient P' = -(1/rho) * (dp/dx)
      const PPrime = (targetQ - QHom) / QPart;

      // Reconstruct axial velocity
      for (let j = 0; j < Nr - 1; j++) {
        this.u[i + 1][j] = uHom[j] + PPrime * uPart[j];
      }
      this.u[i + 1][Nr - 1] = 0.0; // Wall no-slip

      // Update Pressure
      this.p[i + 1] = this.p[i] - rho * dx * PPrime;

      // Compute radial velocity v from continuity: d(rv)/dr = -r * du/dx
      let intRdudx = 0.0;
      for (let j = 1; j < Nr - 1; j++) {
        const dudx1 = (this.u[i + 1][j - 1] - this.u[i][j - 1]) / dx;
        const dudx2 = (this.u[i + 1][j] - this.u[i][j]) / dx;
        intRdudx += 0.5 * (this.r[j - 1] * dudx1 + this.r[j] * dudx2) * dr;
        this.v[i + 1][j] = -intRdudx / this.r[j];
      }
      this.v[i + 1][0] = 0.0;
      this.v[i + 1][Nr - 1] = 0.0;

      // Centerline velocity & wall shear stress
      this.u_centerline[i + 1] = this.u[i + 1][0];
      const duDrWall = (3.0 * this.u[i + 1][Nr - 1] - 4.0 * this.u[i + 1][Nr - 2] + this.u[i + 1][Nr - 3]) / (2.0 * dr);
      this.tau_w[i + 1] = -this.mu * duDrWall;

      if (this.x[i + 1] > 0) {
        const deltaP = this.p[0] - this.p[i + 1];
        this.f_apparent[i + 1] = (deltaP * this.D) / (0.5 * rho * (this.U_in * this.U_in) * this.x[i + 1]);
      }
    }
  }

  thomasSolve(A, B, C, D) {
    const n = B.length;
    const cPrime = new Float64Array(n);
    const dPrime = new Float64Array(n);

    cPrime[0] = C[0] / B[0];
    dPrime[0] = D[0] / B[0];

    for (let k = 1; k < n; k++) {
      const denom = B[k] - A[k] * cPrime[k - 1];
      if (k < n - 1) cPrime[k] = C[k] / denom;
      dPrime[k] = (D[k] - A[k] * dPrime[k - 1]) / denom;
    }

    const x = new Float64Array(n);
    x[n - 1] = dPrime[n - 1];
    for (let k = n - 2; k >= 0; k--) {
      x[k] = dPrime[k] - cPrime[k] * x[k + 1];
    }
    return x;
  }

  // ------------------ Turbo / Jet Colormap for 2D Canvas ------------------
  getColormapRGB(val, minVal, maxVal) {
    const t = Math.max(0, Math.min(1, (val - minVal) / (maxVal - minVal || 1)));
    // Turbo-like colormap approximation
    const r = Math.floor(255 * Math.sin(t * Math.PI * 0.5));
    const g = Math.floor(255 * Math.sin(t * Math.PI));
    const b = Math.floor(255 * Math.cos(t * Math.PI * 0.5));
    return `rgb(${r},${g},${b})`;
  }

  render2DContour(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const w = canvas.width = canvas.parentElement.clientWidth;
    const h = canvas.height = canvas.parentElement.clientHeight || 520;
    ctx.clearRect(0, 0, w, h);

    const padLeft = 70;
    const padRight = 80;
    const padTop = 50;
    const padBottom = 60;

    const plotW = w - padLeft - padRight;
    const plotH = h - padTop - padBottom;
    const halfH = plotH / 2;

    const maxU = 2.05 * this.U_in;

    // Render cells (symmetric about centerline)
    const imgData = ctx.createImageData(plotW, plotH);
    for (let px = 0; px < plotW; px++) {
      const xRatio = px / plotW;
      const i = Math.min(this.Nx - 1, Math.floor(xRatio * (this.Nx - 1)));

      for (let py = 0; py < plotH; py++) {
        // py = 0 is top wall (r = R), py = halfH is axis (r = 0), py = plotH is bottom wall (r = R)
        const distFromCenter = Math.abs(py - halfH) / halfH;
        const j = Math.min(this.Nr - 1, Math.floor(distFromCenter * (this.Nr - 1)));
        const uVal = this.u[i][j];

        const t = Math.max(0, Math.min(1, uVal / maxU));
        // Turbo gradient
        const rColor = Math.floor(255 * Math.min(1, Math.max(0, 1.5 - Math.abs(t - 0.75) * 4)));
        const gColor = Math.floor(255 * Math.min(1, Math.max(0, 1.5 - Math.abs(t - 0.5) * 4)));
        const bColor = Math.floor(255 * Math.min(1, Math.max(0, 1.5 - Math.abs(t - 0.25) * 4)));

        const idx = (py * plotW + px) * 4;
        imgData.data[idx] = rColor;
        imgData.data[idx + 1] = gColor;
        imgData.data[idx + 2] = bColor;
        imgData.data[idx + 3] = 255;
      }
    }
    ctx.putImageData(imgData, padLeft, padTop);

    // Draw Entrance Length Divider
    const xLePixel = padLeft + (this.Le / this.L) * plotW;
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 6]);
    ctx.beginPath();
    ctx.moveTo(xLePixel, padTop);
    ctx.lineTo(xLePixel, padTop + plotH);
    ctx.stroke();
    ctx.setLineDash([]);

    // Pipe Outer Boundaries
    ctx.strokeStyle = "#89b4fa";
    ctx.lineWidth = 2;
    ctx.strokeRect(padLeft, padTop, plotW, plotH);

    // Centerline Axis
    ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]);
    ctx.beginPath();
    ctx.moveTo(padLeft, padTop + halfH);
    ctx.lineTo(padLeft + plotW, padTop + halfH);
    ctx.stroke();
    ctx.setLineDash([]);

    // Text Annotations
    ctx.fillStyle = "#cdd6f4";
    ctx.font = "bold 12px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("ENTRANCE / DEVELOPING REGION", padLeft + (xLePixel - padLeft) / 2, padTop - 14);
    ctx.fillText("FULLY DEVELOPED POISEUILLE FLOW", xLePixel + (padLeft + plotW - xLePixel) / 2, padTop - 14);

    ctx.fillStyle = "#f9e2af";
    ctx.font = "11px sans-serif";
    ctx.fillText(`Le = ${(this.Le * 1e3).toFixed(2)} mm`, xLePixel, padTop + plotH + 20);

    // Axes Labels
    ctx.fillStyle = "#a6adc8";
    ctx.font = "12px sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(`Axial Distance along Pipe x [mm] (Total L = ${(this.L * 1e3).toFixed(2)} mm)`, padLeft + plotW / 2, h - 15);

    ctx.save();
    ctx.translate(22, padTop + halfH);
    ctx.rotate(-Math.PI / 2);
    ctx.textAlign = "center";
    ctx.fillText(`Radial Position r [µm] (R = ±${(this.R * 1e6).toFixed(1)} µm)`, 0, 0);
    ctx.restore();

    // Colorbar on right
    const cbX = padLeft + plotW + 20;
    const cbW = 16;
    for (let py = 0; py < plotH; py++) {
      const t = 1.0 - (py / plotH);
      const rColor = Math.floor(255 * Math.min(1, Math.max(0, 1.5 - Math.abs(t - 0.75) * 4)));
      const gColor = Math.floor(255 * Math.min(1, Math.max(0, 1.5 - Math.abs(t - 0.5) * 4)));
      const bColor = Math.floor(255 * Math.min(1, Math.max(0, 1.5 - Math.abs(t - 0.25) * 4)));
      ctx.fillStyle = `rgb(${rColor},${gColor},${bColor})`;
      ctx.fillRect(cbX, padTop + py, cbW, 1);
    }
    ctx.strokeStyle = "#313244";
    ctx.strokeRect(cbX, padTop, cbW, plotH);

    ctx.fillStyle = "#cdd6f4";
    ctx.font = "10px sans-serif";
    ctx.textAlign = "left";
    ctx.fillText(`${maxU.toFixed(0)} m/s`, cbX + cbW + 6, padTop + 8);
    ctx.fillText(`${(maxU / 2).toFixed(0)} m/s`, cbX + cbW + 6, padTop + halfH + 4);
    ctx.fillText(`0 m/s`, cbX + cbW + 6, padTop + plotH);
  }

  getSummary() {
    const ucEnd = this.u_centerline[this.Nx - 1];
    const acc = (ucEnd / this.u_max_theoretical) * 100.0;
    return (
      `• Inlet Velocity U_in : ${this.U_in.toFixed(1)} m/s (Roll Number)\n` +
      `• Target Reynolds Re  : ${this.Re.toFixed(0)} (Laminar Regime)\n` +
      `• Fluid Properties    : Water @ 20°C (rho=998.2 kg/m³, mu=1.002 mPa·s)\n` +
      `--------------------------------------------------\n` +
      `• Pipe Diameter D     : ${(this.D * 1e6).toFixed(2)} µm (${(this.D * 1e3).toFixed(4)} mm)\n` +
      `• Pipe Radius R       : ${(this.R * 1e6).toFixed(2)} µm\n` +
      `• Entrance Length Le  : ${(this.Le * 1e3).toFixed(3)} mm\n` +
      `• Total Pipe Length L : ${(this.L * 1e3).toFixed(3)} mm (1.60 × Le)\n` +
      `--------------------------------------------------\n` +
      `• Centerline Vel u_c  : ${ucEnd.toFixed(2)} m/s\n` +
      `• Exact Poiseuille    : ${this.u_max_theoretical.toFixed(2)} m/s (2.0 × U_in)\n` +
      `• Numerical Accuracy  : ${acc.toFixed(3)}% Match\n` +
      `• Pressure Gradient   : ${(this.dp_dx_theoretical / 1e6).toFixed(1)} MPa/m\n` +
      `• Wall Shear Stress   : ${(this.tau_w_theoretical / 1e3).toFixed(2)} kPa`
    );
  }
}

