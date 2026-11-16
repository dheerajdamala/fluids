/**
 * Smart Maze-Solving Robot Visualizer Controller
 * AI with Python Course Project
 */

let mazeEngine = null;

document.addEventListener("DOMContentLoaded", () => {
  // Initialize AI Maze Engine
  mazeEngine = new MazeRobotEngine("mazeCanvas");
  mazeEngine.resizeCanvas();
  mazeEngine.render();

  // Attach UI Event Handlers
  initAIClickHandlers();
});

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

  // Reset Robot back to start position
  const btnReset = document.getElementById("btnAiReset");
  if (btnReset) {
    btnReset.addEventListener("click", () => mazeEngine.resetRobot());
  }

  // Clear Path and explored states
  const btnClearPath = document.getElementById("btnAiClearPath");
  if (btnClearPath) {
    btnClearPath.addEventListener("click", () => mazeEngine.resetRobot());
  }

  // Clear Walls & reset grid
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

  // Compare All Algorithms Button
  const btnCompare = document.getElementById("btnAiCompare");
  if (btnCompare) {
    btnCompare.addEventListener("click", () => runAllComparisons(mazeEngine));
  }
}

function closeComparisonModal() {
  const modal = document.getElementById("comparisonModal");
  if (modal) modal.classList.remove("open");
}
