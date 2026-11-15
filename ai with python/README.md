# Smart AI Maze-Solving Robot Visualizer 🤖

An interactive, Python-based application that applies Artificial Intelligence search algorithms (BFS, DFS, Uniform Cost Search, A* Search with Manhattan/Euclidean heuristics, and Greedy Best-First Search) to navigate an autonomous 2D robot through complex mazes and obstacle courses.

Features a modern dark-themed GUI with real-time algorithm state-expansion animations, dynamic path lighting, and smooth directional 2D robot kinematic traversal.

---

## 🌟 Key Features

1. **Six Implemented AI Algorithms**:
   - **A* Search (Manhattan)** — Informed, optimal, and admissible.
   - **A* Search (Euclidean)** — Informed with straight-line distance heuristic.
   - **Breadth-First Search (BFS)** — Uninformed, guarantees shortest path on unit grids.
   - **Depth-First Search (DFS)** — Explores deeply down branches, non-optimal.
   - **Greedy Best-First Search** — Evaluates solely by heuristic $h(n)$ for rapid goal targeting.
   - **Uniform Cost Search (UCS / Dijkstra)** — Cost-optimal search using min-priority queues.

2. **Kinematic 2D Robot Visualization**:
   - Directional chassis that rotates according to the movement vector ($0^\circ, 90^\circ, 180^\circ, 270^\circ$).
   - Directional headlight cone projecting onto upcoming cells.
   - Dual optical sensor eyes with glowing red pupils.
   - Animated track treads and pulsing beacon LED.
   - Continuous breadcrumb trails marking the robot's physical route.
   - Celebratory victory pulse when reaching the goal.

3. **Multiple Maze Generators & Presets**:
   - **Recursive Backtracker** — Perfect winding labyrinth with long corridors.
   - **Randomized Prim's Algorithm** — Organic maze with numerous short branches.
   - **Random Obstacles (25% & 35%)** — Simulates cluttered warehouse or disaster floors.
   - **Presets**: Bottleneck Choke, Spiral Labyrinth, Multi-Room Chambers, and Local Minima Trap.
   - **Blank Canvas** — Clean slate for custom designs.

4. **Interactive Mouse Tools**:
   - Left-click and drag: Draw custom walls.
   - Right-click and drag: Erase walls.
   - Dedicated modes: Move Start point (Green S) and Goal point (Red G) anywhere.

5. **Live Performance Dashboard & Comparison Suite**:
   - Real-time HUD showing Status, Explored States count, Path Length (steps), Search CPU Time (ms), and Robot Progress.
   - **"Run All & Compare" button**: Runs all algorithms on the exact current maze, outputs an ASCII summary table, and generates high-resolution Matplotlib comparison charts.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+ (Tested on Python 3.12)
- Built-in libraries: `tkinter`, `heapq`, `collections`, `time`, `math`
- External library: `matplotlib` (installed for graphical benchmark plots)

```bash
pip install -r requirements.txt
```

---

## 🎮 Running the Application

### 1. Launch the Interactive 2D Visualizer (Default)
Navigate into the folder and run:
```bash
python main.py
```
*(Or specify custom grid dimensions: `python main.py --rows 31 --cols 31`)*

### 2. Run Headless Benchmarking Suite
To run all algorithms without opening the GUI and export comparison charts & CSVs:
```bash
python main.py --benchmark --maze-type recursive
```
Available `--maze-type` choices: `recursive`, `prims`, `random`, `bottleneck`, `spiral`, `multi-room`, `trap`.

### 3. Run Automated Unit & Integration Tests
To verify all algorithm mechanics and robot state logic:
```bash
python test_algorithms.py
```

---

## 🕹 How to Use the Visualizer

1. **Select an Algorithm**: Pick one from the dropdown (e.g., *A\* Search (Manhattan)* or *BFS*).
2. **Generate a Maze**: Select a generator (e.g., *Recursive Backtracker* or *Preset: Bottleneck*) and click **🎲 Generate Maze**.
3. **Customize Obstacles**: Use your mouse to draw walls or adjust Start/Goal positions.
4. **Adjust Speed**: Move the animation speed slider from slow (educational) to turbo fast.
5. **Solve**:
   - Click **▶ START ROBOT SOLVE** to watch the algorithm explore states and see the robot traverse the path.
   - Click **⚡ Instant** to instantly solve without delay.
6. **Compare**: Click **📊 RUN ALL & COMPARE** to benchmark all algorithms side-by-side with comparison charts.

---

## 📁 Project Structure

```
ai with pythin/
├── main.py                 # Application launcher & CLI parser
├── maze.py                 # Grid model, neighbor checks, procedural maze generators
├── algorithms.py           # BFS, DFS, UCS, A*, Greedy Best-First, Heuristic functions
├── robot.py                # 2D Kinematic robot entity, headlights, and drawing logic
├── gui.py                  # Tkinter visualizer, canvas animations, and HUD controls
├── comparison.py           # Multi-algorithm benchmark harness & Matplotlib chart plotter
├── test_algorithms.py      # Automated unit & integration tests
├── requirements.txt        # Package dependencies
├── PROJECT_REPORT.md       # Comprehensive academic project report for 4-student group
└── README.md               # User guide & documentation
```

---

## 👥 Group Project Details (4 Members)

- **Student 1 (Algorithm Architect)**: Formulated state-space mathematical model; implemented BFS, DFS, UCS, and A* Priority Queues.
- **Student 2 (Heuristic Analyst)**: Formulated Manhattan and Euclidean distance heuristics; built benchmark comparison suite & plots.
- **Student 3 (UI & Kinematics Developer)**: Built modern Tkinter UI, custom canvas drawing, and 2D robot kinematics with directional beam.
- **Student 4 (QA & Testing Engineer)**: Implemented procedural maze algorithms (Backtracker & Prim's), stress traps, and unit tests.

