/**
 * Master Application Controller (JavaScript)
 * Manages view switching, conversion triggers, Fluids Chart.js plots, and UI events.
 */

let mazeEngine = null;
let fluidsSolver = null;
let currentView = "ai";

// Fluids Chart.js instances
let chartProfiles = null;
let chartCenterline = null;
let chartPressure = null;

document.addEventListener("DOMContentLoaded", () => {
  // Initialize AI Maze Engine
  mazeEngine = new MazeRobotEngine("mazeCanvas");

  // Initialize Fluids CFD
  runFluidsSimulation();

  // Attach Navigation Listeners
  initNavigation();
  initAIClickHandlers();
  initFluidsClickHandlers();

  // Activate AI Maze directly on load
  switchView("ai");
});

// ------------------ View Navigation & Conversion ------------------
function switchView(viewName) {
  if (viewName !== "ai" && viewName !== "fluids") {
    viewName = "ai";
  }
  currentView = viewName;

  // Toggle pages
  document.querySelectorAll(".page-view").forEach(page => {
    page.classList.remove("active");
  });
  const targetPage = document.getElementById(`page-${viewName}`);
  if (targetPage) targetPage.classList.add("active");

  // Update Nav Button active styles
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.classList.remove("active");
    if (btn.dataset.target === viewName) {
      btn.classList.add("active");
    }
  });

  // Update Master Converter Button
  const convertBtn = document.getElementById("masterConvertBtn");
  if (convertBtn) {
    const swapSvg = `<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="m16 3 4 4-4 4"/><path d="M20 7H4"/><path d="m8 21-4-4 4-4"/><path d="M4 17h16"/></svg>`;
    const arrowSvg = `<svg class="btn-icon-right" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>`;

    if (viewName === "ai") {
      convertBtn.innerHTML = `${swapSvg} <span>Switch to Fluids (Pipe CFD)</span> ${arrowSvg}`;
      convertBtn.dataset.mode = "to-fluids";
    } else {
      convertBtn.innerHTML = `${swapSvg} <span>Switch to AI with Python (Maze Robot)</span> ${arrowSvg}`;
      convertBtn.dataset.mode = "to-ai";
    }
  }

  // Refresh canvases if view was hidden
  if (viewName === "ai" && mazeEngine) {
    setTimeout(() => {
      mazeEngine.resizeCanvas();
      mazeEngine.render();
    }, 50);
  } else if (viewName === "fluids" && fluidsSolver) {
    setTimeout(() => {
      fluidsSolver.render2DContour("contourCanvas");
      updateFluidsCharts();
    }, 50);
  }
}

function toggleMasterConversion() {
  if (currentView === "ai") {
    switchView("fluids");
  } else {
    switchView("ai");
  }
}

function initNavigation() {
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const target = btn.dataset.target;
      if (target) switchView(target);
    });
  });

  const masterBtn = document.getElementById("masterConvertBtn");
  if (masterBtn) {
    masterBtn.addEventListener("click", toggleMasterConversion);
  }
}

// ------------------ AI Maze Engine UI Handlers ------------------
function initAIClickHandlers() {
  // Start Solve
  const btnStart = document.getElementById("btnAiStart");
  if (btnStart) {
    btnStart.addEventListener("click", () => {
      const algo = document.getElementById("selectAiAlgo").value;
      mazeEngine.startSolve(algo);
    });
  }

  // Instant Solve
  const btnInstant = document.getElementById("btnAiInstant");
  if (btnInstant) {
    btnInstant.addEventListener("click", () => {
      const algo = document.getElementById("selectAiAlgo").value;
      mazeEngine.solveInstant(algo);
    });
  }

  // Reset
  const btnReset = document.getElementById("btnAiReset");
  if (btnReset) {
    btnReset.addEventListener("click", () => mazeEngine.resetRobot());
  }

  // Clear Path
  const btnClearPath = document.getElementById("btnAiClearPath");
  if (btnClearPath) {
    btnClearPath.addEventListener("click", () => mazeEngine.resetRobot());
  }

  // Clear Walls
  const btnClearWalls = document.getElementById("btnAiClearWalls");
  if (btnClearWalls) {
    btnClearWalls.addEventListener("click", () => {
      mazeEngine.initGrid();
      mazeEngine.render();
    });
  }

  // Generate Maze
  const btnGen = document.getElementById("btnAiGenMaze");
  if (btnGen) {
    btnGen.addEventListener("click", () => {
      const type = document.getElementById("selectAiMaze").value;
      if (type === "backtracker") mazeEngine.generateRecursiveBacktracker();
      else if (type === "prims") mazeEngine.generatePrims();
      else if (type === "rand25") mazeEngine.generateRandomObstacles(0.25);
      else if (type === "rand35") mazeEngine.generateRandomObstacles(0.35);
      else if (type === "bottleneck") mazeEngine.generatePreset("Bottleneck");
      else if (type === "spiral") mazeEngine.generatePreset("Spiral");
      else if (type === "multiroom") mazeEngine.generatePreset("Multi-Room");
      else if (type === "trap") mazeEngine.generatePreset("Trap");
      else if (type === "blank") { mazeEngine.initGrid(); mazeEngine.render(); }
    });
  }

  // Speed Slider
  const speedSlider = document.getElementById("sliderAiSpeed");
  if (speedSlider) {
    speedSlider.addEventListener("input", (e) => {
      mazeEngine.speed = parseInt(e.target.value);
    });
  }

  // Radio Chips (Edit Mode)
  document.querySelectorAll("input[name='toolMode']").forEach(radio => {
    radio.addEventListener("change", (e) => {
      mazeEngine.mouseMode = e.target.value;
    });
  });

  // Compare All Button
  const btnCompare = document.getElementById("btnAiCompare");
  if (btnCompare) {
    btnCompare.addEventListener("click", () => runAllComparisons(mazeEngine));
  }
}

// ------------------ Fluids CFD UI Handlers ------------------
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

