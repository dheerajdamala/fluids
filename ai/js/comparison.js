/**
 * Multi-Algorithm Benchmark Comparison Module (JavaScript + Chart.js)
 * Executes all 6 algorithms on the current maze grid and visualizes
 * Explored States, Path Length (Steps), and Execution Time.
 */

let comparisonChart = null;

function runAllComparisons(engine) {
  const algos = [
    "A* (Manhattan)",
    "A* (Euclidean)",
    "BFS",
    "DFS",
    "UCS",
    "Greedy Best-First"
  ];

  const results = [];
  for (const name of algos) {
    const res = engine.runAlgorithm(name);
    results.push({
      name,
      success: res.success,
      pathLength: res.success ? Math.max(0, res.path.length - 1) : 0,
      explored: res.explored.length,
      frontier: res.frontier,
      time: res.time
    });
  }

  // Populate Table
  const tbody = document.getElementById("comparisonTableBody");
  if (tbody) {
    tbody.innerHTML = "";
    for (const r of results) {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td style="font-weight: 700; color: #89b4fa;">${r.name}</td>
        <td style="color: ${r.success ? '#a6e3a1' : '#f38ba8'}; font-weight: bold;">${r.success ? 'YES' : 'NO'}</td>
        <td style="font-family: monospace;">${r.pathLength}</td>
        <td style="font-family: monospace;">${r.explored}</td>
        <td style="font-family: monospace;">${r.frontier}</td>
        <td style="font-family: monospace;">${r.time.toFixed(3)}</td>
      `;
      tbody.appendChild(tr);
    }
  }

  // Render Chart.js
  renderComparisonChart(results);

  // Open Modal
  const modal = document.getElementById("comparisonModal");
  if (modal) modal.classList.add("open");
}

function renderComparisonChart(results) {
  const canvas = document.getElementById("comparisonChartCanvas");
  if (!canvas || typeof Chart === "undefined") return;

  const labels = results.map(r => r.name);
  const exploredData = results.map(r => r.explored);
  const pathData = results.map(r => r.pathLength);

  if (comparisonChart) {
    comparisonChart.destroy();
  }

  comparisonChart = new Chart(canvas, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Explored States (Lower = More Efficient)",
          data: exploredData,
          backgroundColor: "rgba(116, 199, 236, 0.7)",
          borderColor: "#74c7ec",
          borderWidth: 1.5,
          yAxisID: "y"
        },
        {
          label: "Path Length (Steps, Optimality)",
          data: pathData,
          backgroundColor: "rgba(249, 226, 175, 0.7)",
          borderColor: "#f9e2af",
          borderWidth: 1.5,
          yAxisID: "y"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: "#cdd6f4", font: { family: "sans-serif", weight: "bold" } }
        }
      },
      scales: {
        x: {
          ticks: { color: "#a6adc8" },
          grid: { color: "rgba(49, 50, 68, 0.5)" }
        },
        y: {
          type: "linear",
          display: true,
          position: "left",
          ticks: { color: "#a6adc8" },
          grid: { color: "rgba(49, 50, 68, 0.5)" }
        }
      }
    }
  });
}

function closeComparisonModal() {
  const modal = document.getElementById("comparisonModal");
  if (modal) modal.classList.remove("open");
}

