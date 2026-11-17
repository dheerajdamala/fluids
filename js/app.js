/**
 * Laminar Water Pipe Flow CFD Simulator Controller
 * Fluid Mechanics Course Assignment
 */

let fluidsSolver = null;

// Chart.js instances
let chartProfiles = null;
let chartCenterline = null;
let chartPressure = null;

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Fluids CFD on load
  runFluidsSimulation();

  // Attach UI Event Handlers
  initFluidsClickHandlers();
});

function initFluidsClickHandlers() {
  const btnRun = document.getElementById("btnFluidsRun");
  if (btnRun) {
    btnRun.addEventListener("click", () => runFluidsSimulation());
  }

  // Fluids Tabs Switcher
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(btn.dataset.pane);
      if (targetPane) targetPane.classList.add("active");

      // Redraw active chart / canvas
      if (btn.dataset.pane === "paneContour") {
        fluidsSolver.render2DContour("contourCanvas");
      } else {
        updateFluidsCharts();
      }
    });
  });
}

function runFluidsSimulation() {
  const roll = parseInt(document.getElementById("inputFluidsRoll")?.value || 67);
  const re = parseFloat(document.getElementById("inputFluidsRe")?.value || 1600);
  const nr = parseInt(document.getElementById("inputFluidsNr")?.value || 80);
  const nx = parseInt(document.getElementById("inputFluidsNx")?.value || 300);

  fluidsSolver = new PipeFlowCFD(roll, re, nr, nx);
  fluidsSolver.solve();

  // Update Summary Text
  const summaryBox = document.getElementById("fluidsSummaryBox");
  if (summaryBox) {
    summaryBox.textContent = fluidsSolver.getSummary();
  }

  // Render 2D Contour
  fluidsSolver.render2DContour("contourCanvas");
  updateFluidsCharts();
}

function updateFluidsCharts() {
  if (!fluidsSolver || typeof Chart === "undefined") return;

  // Chart 1: Radial Profiles
  const ctxProfiles = document.getElementById("chartProfilesCanvas")?.getContext("2d");
  if (ctxProfiles) {
    const stations = [0.0, 0.05, 0.20, 0.50, 1.00, 1.50];
    const colors = ["#74c7ec", "#89b4fa", "#b4befe", "#cba6f7", "#f38ba8", "#fab387"];

    const rNorm = fluidsSolver.r.map(r => (r / fluidsSolver.R).toFixed(2));
    const datasets = [];

    stations.forEach((ratio, idx) => {
      const targetX = ratio * fluidsSolver.Le;
      const i = Math.min(fluidsSolver.Nx - 1, Math.round((targetX / fluidsSolver.L) * (fluidsSolver.Nx - 1)));
      const uData = Array.from(fluidsSolver.u[i]);

      datasets.push({
        label: ratio === 0 ? "Inlet (Slug)" : `x/Le = ${ratio.toFixed(2)}`,
        data: uData,
        borderColor: colors[idx],
        borderWidth: 2,
        fill: false,
        pointRadius: 0
      });
    });

    // Exact Hagen-Poiseuille
    const uPoiseuille = fluidsSolver.r.map(r => 2.0 * fluidsSolver.U_in * (1.0 - Math.pow(r / fluidsSolver.R, 2)));
    datasets.push({
      label: "Theoretical Poiseuille (2.0 × U_in)",
      data: uPoiseuille,
      borderColor: "#f9e2af",
      borderWidth: 2.5,
      borderDash: [5, 5],
      fill: false,
      pointRadius: 0
    });

    if (chartProfiles) chartProfiles.destroy();
    chartProfiles = new Chart(ctxProfiles, {
      type: "line",
      data: { labels: rNorm, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#cdd6f4" } },
          title: { display: true, text: "Evolution of Radial Velocity Profiles u(r) [m/s]", color: "#89b4fa" }
        },
        scales: {
          x: { title: { display: true, text: "Normalized Radial Position (r / R)", color: "#a6adc8" }, ticks: { color: "#a6adc8" } },
          y: { title: { display: true, text: "Axial Velocity u [m/s]", color: "#a6adc8" }, ticks: { color: "#a6adc8" } }
        }
      }
    });
  }

  // Chart 2: Centerline Velocity uc(x)/Uin
  const ctxCenterline = document.getElementById("chartCenterlineCanvas")?.getContext("2d");
  if (ctxCenterline) {
    const xNorm = Array.from(fluidsSolver.x).map(x => (x / fluidsSolver.Le).toFixed(2));
    const ucRatio = Array.from(fluidsSolver.u_centerline).map(uc => (uc / fluidsSolver.U_in).toFixed(3));

    if (chartCenterline) chartCenterline.destroy();
    chartCenterline = new Chart(ctxCenterline, {
      type: "line",
      data: {
        labels: xNorm,
        datasets: [
          {
            label: "Numerical CFD Solution uc(x)/Uin",
            data: ucRatio,
            borderColor: "#89b4fa",
            borderWidth: 2.5,
            fill: false,
            pointRadius: 0
          },
          {
            label: "Theoretical Fully Developed Asymptote (2.0)",
            data: xNorm.map(() => 2.0),
            borderColor: "#f38ba8",
            borderDash: [6, 6],
            borderWidth: 1.8,
            fill: false,
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#cdd6f4" } },
          title: { display: true, text: "Centerline Velocity Acceleration uc(x) / U_in vs Normalized Distance x / Le", color: "#89b4fa" }
        },
        scales: {
          x: { title: { display: true, text: "Normalized Axial Distance (x / Le)", color: "#a6adc8" }, ticks: { color: "#a6adc8" } },
          y: { title: { display: true, text: "uc / U_in", color: "#a6adc8" }, ticks: { color: "#a6adc8" }, min: 0.9, max: 2.1 }
        }
      }
    });
  }

  // Chart 3: Pressure Drop ΔP(x)
  const ctxPressure = document.getElementById("chartPressureCanvas")?.getContext("2d");
  if (ctxPressure) {
    const xMm = Array.from(fluidsSolver.x).map(x => (x * 1e3).toFixed(2));
    const deltaPKPa = Array.from(fluidsSolver.p).map(p => ((fluidsSolver.p[0] - p) / 1e3).toFixed(1));
    const poiseuilleLinear = Array.from(fluidsSolver.x).map(x => ((-fluidsSolver.dp_dx_theoretical * x) / 1e3).toFixed(1));

    if (chartPressure) chartPressure.destroy();
    chartPressure = new Chart(ctxPressure, {
      type: "line",
      data: {
        labels: xMm,
        datasets: [
          {
            label: "Numerical Pressure Drop ΔP(x) [kPa]",
            data: deltaPKPa,
            borderColor: "#cba6f7",
            borderWidth: 2.5,
            fill: false,
            pointRadius: 0
          },
          {
            label: "Linear Poiseuille Reference Slope",
            data: poiseuilleLinear,
            borderColor: "#a6e3a1",
            borderDash: [5, 5],
            borderWidth: 1.8,
            fill: false,
            pointRadius: 0
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: "#cdd6f4" } },
          title: { display: true, text: "Axial Pressure Drop ΔP(x) along Pipe", color: "#cba6f7" }
        },
        scales: {
          x: { title: { display: true, text: "Axial Position x [mm]", color: "#a6adc8" }, ticks: { color: "#a6adc8" } },
          y: { title: { display: true, text: "Pressure Drop ΔP [kPa]", color: "#a6adc8" }, ticks: { color: "#a6adc8" } }
        }
      }
    });
  }
}
