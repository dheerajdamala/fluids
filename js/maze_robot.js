/**
 * Smart 2D Maze-Solving Robot & Search Algorithm Engine (JavaScript/HTML5 Canvas)
 * Implements: BFS, DFS, UCS, A* (Manhattan/Euclidean), Greedy Best-First
 * Procedural Generators: Recursive Backtracker, Prim's, Obstacles, Presets
 * Animated 2D Robot with directional headlights, optical sensors, treads, and trail
 */

const EMPTY = 0;
const WALL = 1;

class MazeRobotEngine {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext("2d");

    this.rows = 25;
    this.cols = 25;
    this.grid = [];
    this.start = { r: 1, c: 1 };
    this.goal = { r: this.rows - 2, c: this.cols - 2 };

    // Robot State
    this.robot = {
      r: 1,
      c: 1,
      angle: 0, // 0 = East, 90 = South, 180 = West, 270 = North
      path: [],
      pathIndex: 0,
      stepsTaken: 0,
      isNavigating: false,
      isFinished: false,
      trail: []
    };

    // Animation & State
    this.isSearching = false;
    this.exploredSet = new Set();
    this.pathCells = new Set();
    this.currentResult = null;
    this.animIndex = 0;
    this.animTimer = null;
    this.pulseFrame = 0;

    // Interaction
    this.mouseMode = "wall"; // "wall", "erase", "start", "goal"
    this.isMouseDown = false;
    this.speed = 65;

    this.initGrid();
    this.attachEvents();
    this.resizeCanvas();
    this.generateRecursiveBacktracker();
  }

  initGrid() {
    this.grid = Array.from({ length: this.rows }, () => Array(this.cols).fill(EMPTY));
    this.start = { r: 1, c: 1 };
    this.goal = { r: this.rows - 2, c: this.cols - 2 };
    this.resetRobot();
  }

  resetRobot() {
    if (this.animTimer) {
      clearTimeout(this.animTimer);
      this.animTimer = null;
    }
    this.robot.r = this.start.r;
    this.robot.c = this.start.c;
    this.robot.angle = 0;
    this.robot.path = [];
    this.robot.pathIndex = 0;
    this.robot.stepsTaken = 0;
    this.robot.isNavigating = false;
    this.robot.isFinished = false;
    this.robot.trail = [{ r: this.start.r, c: this.start.c }];
    this.isSearching = false;
    this.exploredSet.clear();
    this.pathCells.clear();
    this.currentResult = null;
    this.animIndex = 0;
    this.updateHUD("Ready", 0, 0, 0, "0 / 0");
    this.render();
  }

  resizeCanvas() {
    const parent = this.canvas.parentElement;
    const w = parent.clientWidth - 10;
    const h = parent.clientHeight - 10;
    const size = Math.max(10, Math.floor(Math.min((w - 20) / this.cols, (h - 20) / this.rows)));
    this.cellSize = size;
    this.canvas.width = this.cols * size;
    this.canvas.height = this.rows * size;
    this.render();
  }

  attachEvents() {
    window.addEventListener("resize", () => this.resizeCanvas());

    this.canvas.addEventListener("mousedown", (e) => {
      this.isMouseDown = true;
      this.handleMouse(e);
    });

    this.canvas.addEventListener("mousemove", (e) => {
      if (this.isMouseDown) this.handleMouse(e);
    });

    window.addEventListener("mouseup", () => {
      this.isMouseDown = false;
    });

    this.canvas.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      const coords = this.getCoords(e);
      if (coords && !this.isSearching && !this.robot.isNavigating) {
        this.setWall(coords.r, coords.c, false);
        this.render();
      }
    });
  }

  getCoords(e) {
    const rect = this.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const c = Math.floor(x / this.cellSize);
    const r = Math.floor(y / this.cellSize);
    if (r >= 0 && r < this.rows && c >= 0 && c < this.cols) {
      return { r, c };
    }
    return null;
  }

  handleMouse(e) {
    if (this.isSearching || this.robot.isNavigating) return;
    const pt = this.getCoords(e);
    if (!pt) return;

    if (e.buttons === 2) {
      this.setWall(pt.r, pt.c, false);
      this.render();
      return;
    }

    if (this.mouseMode === "wall") {
      this.setWall(pt.r, pt.c, true);
    } else if (this.mouseMode === "erase") {
      this.setWall(pt.r, pt.c, false);
    } else if (this.mouseMode === "start") {
      if (!(pt.r === this.goal.r && pt.c === this.goal.c)) {
        this.start = { r: pt.r, c: pt.c };
        this.resetRobot();
      }
    } else if (this.mouseMode === "goal") {
      if (!(pt.r === this.start.r && pt.c === this.start.c)) {
        this.goal = { r: pt.r, c: pt.c };
        this.resetRobot();
      }
    }
    this.render();
  }

  setWall(r, c, isWall) {
    if ((r === this.start.r && c === this.start.c) || (r === this.goal.r && c === this.goal.c)) {
      return;
    }
    this.grid[r][c] = isWall ? WALL : EMPTY;
  }

  // ------------------ Maze Generators ------------------
  generateRecursiveBacktracker() {
    this.grid = Array.from({ length: this.rows }, () => Array(this.cols).fill(WALL));
    const stack = [{ r: 1, c: 1 }];
    this.grid[1][1] = EMPTY;
    const visited = new Set(["1,1"]);

    while (stack.length > 0) {
      const { r, c } = stack[stack.length - 1];
      const neighbors = [];
      const dirs = [[-2, 0], [2, 0], [0, -2], [0, 2]];

      for (const [dr, dc] of dirs) {
        const nr = r + dr;
        const nc = c + dc;
        if (nr > 0 && nr < this.rows - 1 && nc > 0 && nc < this.cols - 1) {
          if (!visited.has(`${nr},${nc}`)) {
            neighbors.push({ nr, nc, dr, dc });
          }
        }
      }

      if (neighbors.length > 0) {
        const chosen = neighbors[Math.floor(Math.random() * neighbors.length)];
        this.grid[r + chosen.dr / 2][c + chosen.dc / 2] = EMPTY;
        this.grid[chosen.nr][chosen.nc] = EMPTY;
        visited.add(`${chosen.nr},${chosen.nc}`);
        stack.push({ r: chosen.nr, c: chosen.nc });
      } else {
        stack.pop();
      }
    }

    this.start = { r: 1, c: 1 };
    this.goal = { r: this.rows - 2, c: this.cols - 2 };
    this.grid[this.start.r][this.start.c] = EMPTY;
    this.grid[this.goal.r][this.goal.c] = EMPTY;
    this.resetRobot();
  }

  generatePrims() {
    this.grid = Array.from({ length: this.rows }, () => Array(this.cols).fill(WALL));
    this.grid[1][1] = EMPTY;
    const walls = [];

    for (const [dr, dc] of [[-2, 0], [2, 0], [0, -2], [0, 2]]) {
      const nr = 1 + dr;
      const nc = 1 + dc;
      if (nr > 0 && nr < this.rows - 1 && nc > 0 && nc < this.cols - 1) {
        walls.push({ nr, nc, mr: 1 + dr / 2, mc: 1 + dc / 2 });
      }
    }

    while (walls.length > 0) {
      const idx = Math.floor(Math.random() * walls.length);
      const { nr, nc, mr, mc } = walls.splice(idx, 1)[0];

      if (this.grid[nr][nc] === WALL) {
        this.grid[mr][mc] = EMPTY;
        this.grid[nr][nc] = EMPTY;

        for (const [dr, dc] of [[-2, 0], [2, 0], [0, -2], [0, 2]]) {
          const nnr = nr + dr;
          const nnc = nc + dc;
          if (nnr > 0 && nnr < this.rows - 1 && nnc > 0 && nnc < this.cols - 1) {
            if (this.grid[nnr][nnc] === WALL) {
              walls.push({ nr: nnr, nc: nnc, mr: nr + dr / 2, mc: nc + dc / 2 });
            }
          }
        }
      }
    }
    this.start = { r: 1, c: 1 };
    this.goal = { r: this.rows - 2, c: this.cols - 2 };
    this.resetRobot();
  }

  generateRandomObstacles(density = 0.25) {
    this.initGrid();
    for (let r = 0; r < this.rows; r++) {
      for (let c = 0; c < this.cols; c++) {
        if (!((r === this.start.r && c === this.start.c) || (r === this.goal.r && c === this.goal.c))) {
          if (Math.random() < density) {
            this.grid[r][c] = WALL;
          }
        }
      }
    }
    this.resetRobot();
  }

  generatePreset(name) {
    this.initGrid();
    const rMid = Math.floor(this.rows / 2);
    const cMid = Math.floor(this.cols / 2);

    if (name === "Bottleneck") {
      for (let r = 0; r < this.rows; r++) {
        if (r !== rMid) this.grid[r][cMid] = WALL;
      }
      this.start = { r: rMid, c: 2 };
      this.goal = { r: rMid, c: this.cols - 3 };
    } else if (name === "Spiral") {
      let top = 0, bottom = this.rows - 1, left = 0, right = this.cols - 1;
      const step = 2;
      while (top + step < bottom && left + step < right) {
        for (let c = left + step; c <= right - step; c++) this.grid[top + step][c] = WALL;
        for (let r = top + step; r <= bottom - step; r++) this.grid[r][right - step] = WALL;
        for (let c = right - step; c >= left + step; c--) this.grid[bottom - step][c] = WALL;
        for (let r = bottom - step; r >= top + step + 2; r--) this.grid[r][left + step] = WALL;
        top += step + 1; bottom -= step + 1; left += step + 1; right -= step + 1;
      }
      this.start = { r: 1, c: 1 };
      this.goal = { r: rMid, c: cMid };
    } else if (name === "Multi-Room") {
      for (let r = 0; r < this.rows; r++) {
        if (r !== Math.floor(this.rows / 4) && r !== Math.floor(3 * this.rows / 4)) {
          this.grid[r][cMid] = WALL;
        }
      }
      for (let c = 0; c < this.cols; c++) {
        if (c !== Math.floor(this.cols / 4) && c !== Math.floor(3 * this.cols / 4)) {
          this.grid[rMid][c] = WALL;
        }
      }
      this.start = { r: 2, c: 2 };
      this.goal = { r: this.rows - 3, c: this.cols - 3 };
    } else if (name === "Trap") {
      for (let r = rMid - 4; r <= rMid + 4; r++) this.grid[r][cMid + 3] = WALL;
      for (let c = cMid - 4; c <= cMid + 4; c++) {
        this.grid[rMid - 4][c] = WALL;
        this.grid[rMid + 4][c] = WALL;
      }
      this.start = { r: rMid, c: cMid };
      this.goal = { r: rMid, c: cMid + 6 };
    }
    this.resetRobot();
  }

  // ------------------ Search Algorithms ------------------
  getNeighbors(r, c) {
    const list = [];
    const dirs = [[-1, 0], [1, 0], [0, -1], [0, 1]];
    for (const [dr, dc] of dirs) {
      const nr = r + dr;
      const nc = c + dc;
      if (nr >= 0 && nr < this.rows && nc >= 0 && nc < this.cols && this.grid[nr][nc] !== WALL) {
        list.push({ r: nr, c: nc });
      }
    }
    return list;
  }

  manhattan(p1, p2) {
    return Math.abs(p1.r - p2.r) + Math.abs(p1.c - p2.c);
  }

  euclidean(p1, p2) {
    return Math.hypot(p1.r - p2.r, p1.c - p2.c);
  }

  runAlgorithm(algoName) {
    const t0 = performance.now();
    const start = this.start;
    const goal = this.goal;

    if (start.r === goal.r && start.c === goal.c) {
      return { success: true, path: [start], explored: [start], frontier: 1, time: 0 };
    }

    if (algoName === "BFS") return this.runBFS(start, goal, t0);
    if (algoName === "DFS") return this.runDFS(start, goal, t0);
    if (algoName === "UCS") return this.runUCS(start, goal, t0);
    if (algoName === "A* (Manhattan)") return this.runAStar(start, goal, this.manhattan, t0);
    if (algoName === "A* (Euclidean)") return this.runAStar(start, goal, this.euclidean, t0);
    if (algoName === "Greedy Best-First") return this.runGreedy(start, goal, this.manhattan, t0);

    return this.runAStar(start, goal, this.manhattan, t0);
  }

  runBFS(start, goal, t0) {
    const queue = [start];
    const visited = new Set([`${start.r},${start.c}`]);
    const parent = new Map();
    const explored = [];
    let maxFrontier = 1;

    while (queue.length > 0) {
      maxFrontier = Math.max(maxFrontier, queue.length);
      const curr = queue.shift();
      explored.push(curr);

      if (curr.r === goal.r && curr.c === goal.c) {
        const path = this.reconstructPath(parent, start, goal);
        return { success: true, path, explored, frontier: maxFrontier, time: performance.now() - t0 };
      }

      for (const n of this.getNeighbors(curr.r, curr.c)) {
        const key = `${n.r},${n.c}`;
        if (!visited.has(key)) {
          visited.add(key);
          parent.set(key, curr);
          queue.push(n);
        }
      }
    }
    return { success: false, path: [], explored, frontier: maxFrontier, time: performance.now() - t0 };
  }

  runDFS(start, goal, t0) {
    const stack = [start];
    const visited = new Set([`${start.r},${start.c}`]);
    const parent = new Map();
    const explored = [];
    let maxFrontier = 1;

    while (stack.length > 0) {
      maxFrontier = Math.max(maxFrontier, stack.length);
      const curr = stack.pop();
      explored.push(curr);

      if (curr.r === goal.r && curr.c === goal.c) {
        const path = this.reconstructPath(parent, start, goal);
        return { success: true, path, explored, frontier: maxFrontier, time: performance.now() - t0 };
      }

      for (const n of this.getNeighbors(curr.r, curr.c)) {
        const key = `${n.r},${n.c}`;
        if (!visited.has(key)) {
          visited.add(key);
          parent.set(key, curr);
          stack.push(n);
        }
      }
    }
    return { success: false, path: [], explored, frontier: maxFrontier, time: performance.now() - t0 };
  }

  runUCS(start, goal, t0) {
    // Min-Priority Queue on gCost
    const pq = [{ cost: 0, node: start }];
    const gCosts = new Map([[`${start.r},${start.c}`, 0]]);
    const visited = new Set();
    const parent = new Map();
    const explored = [];
    let maxFrontier = 1;

    while (pq.length > 0) {
      maxFrontier = Math.max(maxFrontier, pq.length);
      pq.sort((a, b) => a.cost - b.cost);
      const { cost, node } = pq.shift();
      const key = `${node.r},${node.c}`;

      if (visited.has(key)) continue;
      visited.add(key);
      explored.push(node);

      if (node.r === goal.r && node.c === goal.c) {
        const path = this.reconstructPath(parent, start, goal);
        return { success: true, path, explored, frontier: maxFrontier, time: performance.now() - t0 };
      }

      for (const n of this.getNeighbors(node.r, node.c)) {
        const nKey = `${n.r},${n.c}`;
        const tentativeG = cost + 1;
        if (!gCosts.has(nKey) || tentativeG < gCosts.get(nKey)) {
          gCosts.set(nKey, tentativeG);
          parent.set(nKey, node);
          pq.push({ cost: tentativeG, node: n });
        }
      }
    }
    return { success: false, path: [], explored, frontier: maxFrontier, time: performance.now() - t0 };
  }

  runAStar(start, goal, hFunc, t0) {
    const pq = [{ f: hFunc(start, goal), g: 0, node: start }];
    const gCosts = new Map([[`${start.r},${start.c}`, 0]]);
    const visited = new Set();
    const parent = new Map();
    const explored = [];
    let maxFrontier = 1;

    while (pq.length > 0) {
      maxFrontier = Math.max(maxFrontier, pq.length);
      pq.sort((a, b) => a.f - b.f);
      const { g, node } = pq.shift();
      const key = `${node.r},${node.c}`;

      if (visited.has(key)) continue;
      visited.add(key);
      explored.push(node);

      if (node.r === goal.r && node.c === goal.c) {
        const path = this.reconstructPath(parent, start, goal);
        return { success: true, path, explored, frontier: maxFrontier, time: performance.now() - t0 };
      }

      for (const n of this.getNeighbors(node.r, node.c)) {
        const nKey = `${n.r},${n.c}`;
        const tentativeG = g + 1;
        if (!gCosts.has(nKey) || tentativeG < gCosts.get(nKey)) {
          gCosts.set(nKey, tentativeG);
          parent.set(nKey, node);
          const f = tentativeG + hFunc(n, goal);
          pq.push({ f, g: tentativeG, node: n });
        }
      }
    }
    return { success: false, path: [], explored, frontier: maxFrontier, time: performance.now() - t0 };
  }

  runGreedy(start, goal, hFunc, t0) {
    const pq = [{ h: hFunc(start, goal), node: start }];
    const visited = new Set([`${start.r},${start.c}`]);
    const parent = new Map();
    const explored = [];
    let maxFrontier = 1;

    while (pq.length > 0) {
      maxFrontier = Math.max(maxFrontier, pq.length);
      pq.sort((a, b) => a.h - b.h);
      const { node } = pq.shift();
      explored.push(node);

      if (node.r === goal.r && node.c === goal.c) {
        const path = this.reconstructPath(parent, start, goal);
        return { success: true, path, explored, frontier: maxFrontier, time: performance.now() - t0 };
      }

      for (const n of this.getNeighbors(node.r, node.c)) {
        const nKey = `${n.r},${n.c}`;
        if (!visited.has(nKey)) {
          visited.add(nKey);
          parent.set(nKey, node);
          pq.push({ h: hFunc(n, goal), node: n });
        }
      }
    }
    return { success: false, path: [], explored, frontier: maxFrontier, time: performance.now() - t0 };
  }

  reconstructPath(parentMap, start, goal) {
    const path = [];
    let curr = goal;
    while (curr) {
      path.push(curr);
      curr = parentMap.get(`${curr.r},${curr.c}`);
    }
    path.reverse();
    return (path.length > 0 && path[0].r === start.r && path[0].c === start.c) ? path : [];
  }

  // ------------------ Visualizer Execution ------------------
  startSolve(algoName) {
    if (this.isSearching || this.robot.isNavigating) return;
    this.resetRobot();

    this.updateHUD("Searching...", 0, 0, 0, "0 / 0");
    const res = this.runAlgorithm(algoName);
    this.currentResult = res;

    this.updateHUD(
      res.success ? "Searching..." : "NO PATH FOUND",
      res.explored.length,
      res.success ? res.path.length - 1 : 0,
      res.time.toFixed(2),
      `0 / ${res.success ? res.path.length - 1 : 0}`
    );

    if (!res.success) {
      alert(`No valid path found! Goal is completely blocked by walls.`);
      return;
    }

    this.isSearching = true;
    this.animIndex = 0;
    this.stepSearchAnimation();
  }

  stepSearchAnimation() {
    if (!this.isSearching || !this.currentResult) return;
    const batch = this.speed < 40 ? 1 : (this.speed < 70 ? 2 : 5);

    for (let i = 0; i < batch; i++) {
      if (this.animIndex < this.currentResult.explored.length) {
        const pt = this.currentResult.explored[this.animIndex++];
        this.exploredSet.add(`${pt.r},${pt.c}`);
      } else {
        break;
      }
    }
    this.render();

    if (this.animIndex < this.currentResult.explored.length) {
      const delay = Math.max(4, Math.floor(180 - (this.speed / 100) * 175));
      this.animTimer = setTimeout(() => this.stepSearchAnimation(), delay);
    } else {
      // Done searching, reveal path & start robot
      this.isSearching = false;
      this.pathCells = new Set(this.currentResult.path.map(p => `${p.r},${p.c}`));
      this.updateHUD("Navigating...", this.currentResult.explored.length, this.currentResult.path.length - 1, this.currentResult.time.toFixed(2), `0 / ${this.currentResult.path.length - 1}`);
      this.render();

      this.robot.path = this.currentResult.path;
      this.robot.pathIndex = 0;
      this.robot.stepsTaken = 0;
      this.robot.isNavigating = true;
      this.animTimer = setTimeout(() => this.stepRobotAnimation(), 120);
    }
  }

  stepRobotAnimation() {
    if (!this.robot.isNavigating || !this.robot.path || this.robot.path.length <= 1) return;

    if (this.robot.pathIndex < this.robot.path.length - 1) {
      this.robot.pathIndex++;
      const next = this.robot.path[this.robot.pathIndex];
      const dr = next.r - this.robot.r;
      const dc = next.c - this.robot.c;

      if (dc > 0) this.robot.angle = 0;
      else if (dr > 0) this.robot.angle = 90;
      else if (dc < 0) this.robot.angle = 180;
      else if (dr < 0) this.robot.angle = 270;

      this.robot.r = next.r;
      this.robot.c = next.c;
      this.robot.stepsTaken++;
      this.robot.trail.push(next);
      this.pulseFrame++;

      this.updateHUD(
        "Navigating...",
        this.currentResult.explored.length,
        this.currentResult.path.length - 1,
        this.currentResult.time.toFixed(2),
        `${this.robot.stepsTaken} / ${this.currentResult.path.length - 1}`
      );
      this.render();

      const delay = Math.max(30, Math.floor((180 - (this.speed / 100) * 175) * 1.5));
      this.animTimer = setTimeout(() => this.stepRobotAnimation(), delay);
    } else {
      this.robot.isNavigating = false;
      this.robot.isFinished = true;
      this.updateHUD(
        "GOAL REACHED! 🏆",
        this.currentResult.explored.length,
        this.currentResult.path.length - 1,
        this.currentResult.time.toFixed(2),
        `${this.robot.stepsTaken} / ${this.currentResult.path.length - 1}`
      );
      this.startCelebrationPulse();
    }
  }

  startCelebrationPulse() {
    let frame = 0;
    const pulseLoop = () => {
      if (frame < 16 && !this.isSearching && !this.robot.isNavigating) {
        this.pulseFrame = frame++;
        this.render();
        setTimeout(pulseLoop, 75);
      }
    };
    pulseLoop();
  }

  solveInstant(algoName) {
    this.resetRobot();
    const res = this.runAlgorithm(algoName);
    this.currentResult = res;
    this.exploredSet = new Set(res.explored.map(p => `${p.r},${p.c}`));

    if (res.success) {
      this.pathCells = new Set(res.path.map(p => `${p.r},${p.c}`));
      this.robot.r = this.goal.r;
      this.robot.c = this.goal.c;
      this.robot.trail = res.path;
      this.robot.isFinished = true;
      this.updateHUD("GOAL REACHED! ⚡", res.explored.length, res.path.length - 1, res.time.toFixed(2), `${res.path.length - 1} / ${res.path.length - 1}`);
    } else {
      this.updateHUD("NO PATH FOUND", res.explored.length, 0, res.time.toFixed(2), "0 / 0");
    }
    this.render();
  }

  updateHUD(status, explored, pathLen, time, steps) {
    const elStatus = document.getElementById("hudStatus");
    const elExp = document.getElementById("hudExplored");
    const elPath = document.getElementById("hudPath");
    const elTime = document.getElementById("hudTime");
    const elSteps = document.getElementById("hudSteps");

    if (elStatus) elStatus.textContent = status;
    if (elExp) elExp.textContent = `${explored} states`;
    if (elPath) elPath.textContent = `${pathLen} steps`;
    if (elTime) elTime.textContent = `${time} ms`;
    if (elSteps) elSteps.textContent = steps;
  }

  // ------------------ Canvas Rendering ------------------
  render() {
    const ctx = this.ctx;
    const cs = this.cellSize;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw Grid Cells
    for (let r = 0; r < this.rows; r++) {
      for (let c = 0; c < this.cols; c++) {
        const x = c * cs;
        const y = r * cs;
        const key = `${r},${c}`;

        let fill = "#1e1e2e";
        let stroke = "#232336";

        if (this.grid[r][c] === WALL) {
          fill = "#45475a";
          stroke = "#585b70";
        } else if (r === this.start.r && c === this.start.c) {
          fill = "#a6e3a1";
        } else if (r === this.goal.r && c === this.goal.c) {
          fill = "#f38ba8";
        } else if (this.pathCells.has(key)) {
          fill = "#f9e2af";
        } else if (this.robot.trail.some(p => p.r === r && p.c === c)) {
          fill = "#eba0ac";
        } else if (this.exploredSet.has(key)) {
          fill = "#74c7ec";
        }

        ctx.fillStyle = fill;
        ctx.fillRect(x, y, cs, cs);
        ctx.strokeStyle = stroke;
        ctx.lineWidth = 1;
        ctx.strokeRect(x, y, cs, cs);

        // Start / Goal badges
        if (r === this.start.r && c === this.start.c) {
          ctx.fillStyle = "#11111b";
          ctx.font = `bold ${Math.max(10, Math.floor(cs * 0.45))}px sans-serif`;
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText("S", x + cs / 2, y + cs / 2);
        } else if (r === this.goal.r && c === this.goal.c) {
          ctx.fillStyle = "#ffffff";
          ctx.font = `bold ${Math.max(10, Math.floor(cs * 0.45))}px sans-serif`;
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText("G", x + cs / 2, y + cs / 2);
        }
      }
    }

    // Path Connecting Line
    if (this.currentResult && this.currentResult.path && this.currentResult.path.length > 1 && this.pathCells.size > 0) {
      ctx.beginPath();
      ctx.strokeStyle = "#fab387";
      ctx.lineWidth = Math.max(2, Math.floor(cs * 0.22));
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      for (let i = 0; i < this.currentResult.path.length; i++) {
        const p = this.currentResult.path[i];
        const px = p.c * cs + cs / 2;
        const py = p.r * cs + cs / 2;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.stroke();
    }

    // 2D Robot Drawing
    this.drawRobot(ctx, cs);
  }

  drawRobot(ctx, cs) {
    const cx = this.robot.c * cs + cs / 2;
    const cy = this.robot.r * cs + cs / 2;
    const rad = cs * 0.42;
    const angleRad = (this.robot.angle * Math.PI) / 180;

    // 1. Headlight beam cone
    const beamDist = cs * 1.35;
    const spread = 0.45; // radians
    ctx.save();
    ctx.fillStyle = "rgba(255, 245, 157, 0.35)";
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + beamDist * Math.cos(angleRad - spread), cy + beamDist * Math.sin(angleRad - spread));
    ctx.lineTo(cx + beamDist * Math.cos(angleRad + spread), cy + beamDist * Math.sin(angleRad + spread));
    ctx.closePath();
    ctx.fill();
    ctx.restore();

    // 2. Treads (tracks on both sides)
    const perpRad = angleRad + Math.PI / 2;
    const treadDist = rad * 0.82;
    for (const sign of [-1, 1]) {
      const tx = cx + sign * treadDist * Math.cos(perpRad);
      const ty = cy + sign * treadDist * Math.sin(perpRad);
      ctx.fillStyle = "#263238";
      ctx.strokeStyle = "#37474f";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(tx, ty, rad * 0.32, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    }

    // 3. Main Metallic Cyan Chassis
    ctx.fillStyle = "#00e5ff";
    ctx.strokeStyle = "#00838f";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, rad, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // 4. Inner Circuit Core
    ctx.fillStyle = "#0097a7";
    ctx.beginPath();
    ctx.arc(cx, cy, rad * 0.65, 0, Math.PI * 2);
    ctx.fill();

    // 5. Directional Sensor Eyes / Camera
    const eyeOffset = rad * 0.45;
    const eyeCx = cx + eyeOffset * Math.cos(angleRad);
    const eyeCy = cy + eyeOffset * Math.sin(angleRad);
    const eyeRadius = rad * 0.28;

    for (const side of [-1, 1]) {
      const lx = eyeCx + side * (rad * 0.28) * Math.cos(perpRad);
      const ly = eyeCy + side * (rad * 0.28) * Math.sin(perpRad);

      ctx.fillStyle = "#ffffff";
      ctx.strokeStyle = "#004d40";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(lx, ly, eyeRadius, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      // Glowing pupil
      ctx.fillStyle = "#ff1744";
      ctx.beginPath();
      ctx.arc(lx, ly, eyeRadius * 0.45, 0, Math.PI * 2);
      ctx.fill();
    }

    // 6. Antenna Beacon LED
    const beaconColor = Math.floor(this.pulseFrame / 3) % 2 === 0 ? "#ff5252" : "#ffd700";
    ctx.fillStyle = beaconColor;
    ctx.strokeStyle = "#b71c1c";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(cx, cy, rad * 0.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // 7. Victory celebration pulse
    if (this.robot.isFinished) {
      const pulseR = rad * 1.3 + (this.pulseFrame % 8) * 3;
      ctx.strokeStyle = "#00e676";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(cx, cy, pulseR, 0, Math.PI * 2);
      ctx.stroke();
    }
  }
}

