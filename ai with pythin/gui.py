"""
Interactive Graphical User Interface and Visualizer for AI Maze Solving Robot.
Built using Tkinter Canvas with a modern dark theme.
Visualizes algorithm node expansions, path reconstruction,
and smooth 2D robot physical traversal with directional kinematics.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
from maze import Maze, EMPTY, WALL, START, GOAL
from algorithms import (
    ALGORITHMS,
    manhattan_distance,
    euclidean_distance,
    bfs,
    dfs,
    uniform_cost_search,
    a_star,
    greedy_best_first_search,
)
from robot import Robot
from comparison import run_all_comparisons, print_comparison_table, generate_comparison_plots

class MazeRobotApp:
    def __init__(self, root, rows=25, cols=25):
        self.root = root
        self.root.title("AI Maze-Solving Robot Visualizer - Autonomous Navigation")
        self.root.geometry("1180x820")
        self.root.minsize(980, 720)
        self.root.configure(bg="#1E1E2E")

        self.rows = rows
        self.cols = cols
        self.maze = Maze(rows, cols)
        self.robot = Robot(self.maze.start)

        # State management
        self.is_searching = False
        self.is_animating_robot = False
        self.paused = False
        self.anim_after_id = None
        self.pulse_frame = 0

        # Current search results
        self.current_result = None
        self.explored_set = set()
        self.path_cells = set()
        self.anim_step_index = 0

        # Mouse interaction mode
        self.mouse_mode = tk.StringVar(value="wall")  # "wall", "erase", "start", "goal"

        # Theme Colors
        self.colors = {
            "bg": "#1E1E2E",
            "panel_bg": "#181825",
            "canvas_bg": "#11111B",
            "grid_line": "#232336",
            "empty": "#1E1E2E",
            "wall": "#45475A",
            "wall_border": "#585B70",
            "start": "#A6E3A1",
            "goal": "#F38BA8",
            "explored_early": "#74C7EC",
            "explored_late": "#CBA6F7",
            "frontier": "#F9E2AF",
            "path": "#F9E2AF",
            "path_line": "#FAB387",
            "trail": "#EBA0AC",
            "text": "#CDD6F4",
            "subtext": "#BAC2DE",
            "accent": "#89B4FA",
            "success": "#A6E3A1",
            "danger": "#F38BA8"
        }

        self._build_ui()
        self.maze.generate_recursive_backtracker()
        self.robot.reset(self.maze.start)
        self.draw_maze()

    def _build_ui(self):
        # Main layout: Left controls panel, Right canvas + stats
        self.main_container = tk.Frame(self.root, bg=self.colors["bg"])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Left Sidebar (Controls)
        self.sidebar = tk.Frame(self.main_container, bg=self.colors["panel_bg"], width=320, relief=tk.FLAT)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        self.sidebar.pack_propagate(False)

        # Right Main Panel (Canvas & HUD)
        self.right_panel = tk.Frame(self.main_container, bg=self.colors["bg"])
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_sidebar_widgets()
        self._build_right_panel_widgets()

    def _build_sidebar_widgets(self):
        pad_x, pad_y = 12, 6

        # App Title & Subtitle
        title_lbl = tk.Label(
            self.sidebar, text="🤖 SMART MAZE ROBOT",
            font=("Segoe UI", 15, "bold"), fg="#89B4FA", bg=self.colors["panel_bg"]
        )
        title_lbl.pack(anchor="w", padx=pad_x, pady=(12, 2))

        sub_lbl = tk.Label(
            self.sidebar, text="Autonomous AI Pathfinding & Kinematics",
            font=("Segoe UI", 8), fg=self.colors["subtext"], bg=self.colors["panel_bg"]
        )
        sub_lbl.pack(anchor="w", padx=pad_x, pady=(0, 6))

        # Quick Switch to Fluids Button
        switch_btn = tk.Button(
            self.sidebar, text="🌊 Switch to Fluids (Pipe CFD) ➔",
            font=("Segoe UI", 9, "bold"), bg="#89B4FA", fg="#11111B",
            activebackground="#74C7EC", activeforeground="#11111B",
            relief=tk.FLAT, cursor="hand2", pady=4,
            command=self._launch_fluids_suite
        )
        switch_btn.pack(fill=tk.X, padx=pad_x, pady=(0, 10))

        # --- Section 1: Algorithm Selection ---
        sec1 = tk.LabelFrame(
            self.sidebar, text=" AI Search Algorithm ",
            font=("Segoe UI", 9, "bold"), fg=self.colors["accent"], bg=self.colors["panel_bg"]
        )
        sec1.pack(fill=tk.X, padx=pad_x, pady=pad_y)

        self.algo_var = tk.StringVar(value="A* Search (Manhattan)")
        self.algo_dropdown = ttk.Combobox(
            sec1, textvariable=self.algo_var, state="readonly",
            values=list(ALGORITHMS.keys()), font=("Segoe UI", 9)
        )
        self.algo_dropdown.pack(fill=tk.X, padx=8, pady=8)
        self.algo_dropdown.bind("<<ComboboxSelected>>", self._on_algo_changed)

        # Algorithm Details description snippet
        self.algo_desc_lbl = tk.Label(
            sec1, text=self._get_algo_desc(self.algo_var.get()),
            font=("Segoe UI", 8), fg=self.colors["subtext"], bg=self.colors["panel_bg"],
            wraplength=270, justify="left"
        )
        self.algo_desc_lbl.pack(fill=tk.X, padx=8, pady=(0, 8))

        # --- Section 2: Maze Generation ---
        sec2 = tk.LabelFrame(
            self.sidebar, text=" Maze & Environment ",
            font=("Segoe UI", 9, "bold"), fg=self.colors["accent"], bg=self.colors["panel_bg"]
        )
        sec2.pack(fill=tk.X, padx=pad_x, pady=pad_y)

        self.maze_var = tk.StringVar(value="Recursive Backtracker")
        maze_opts = [
            "Recursive Backtracker",
            "Prim's Algorithm",
            "Random Obstacles (25%)",
            "Random Obstacles (35%)",
            "Preset: Bottleneck",
            "Preset: Spiral",
            "Preset: Multi-Room",
            "Preset: Trap / Local Minima",
            "Blank Canvas"
        ]
        self.maze_dropdown = ttk.Combobox(
            sec2, textvariable=self.maze_var, state="readonly",
            values=maze_opts, font=("Segoe UI", 9)
        )
        self.maze_dropdown.pack(fill=tk.X, padx=8, pady=(8, 4))

        gen_btn = tk.Button(
            sec2, text="🎲 Generate Maze", font=("Segoe UI", 9, "bold"),
            bg="#313244", fg="#CDD6F4", activebackground="#45475A", activeforeground="#FFFFFF",
            relief=tk.FLAT, cursor="hand2", command=self.generate_selected_maze
        )
        gen_btn.pack(fill=tk.X, padx=8, pady=(4, 8))

        # --- Section 3: Interactive Drawing Mode ---
        sec3 = tk.LabelFrame(
            self.sidebar, text=" Interactive Grid Tool ",
            font=("Segoe UI", 9, "bold"), fg=self.colors["accent"], bg=self.colors["panel_bg"]
        )
        sec3.pack(fill=tk.X, padx=pad_x, pady=pad_y)

        tool_frame = tk.Frame(sec3, bg=self.colors["panel_bg"])
        tool_frame.pack(fill=tk.X, padx=8, pady=4)

        modes = [("Draw Wall", "wall"), ("Erase", "erase"), ("Set Start", "start"), ("Set Goal", "goal")]
        for i, (m_text, m_val) in enumerate(modes):
            rb = tk.Radiobutton(
                tool_frame, text=m_text, variable=self.mouse_mode, value=m_val,
                font=("Segoe UI", 8), fg=self.colors["text"], bg=self.colors["panel_bg"],
                selectcolor="#313244", activebackground=self.colors["panel_bg"], activeforeground="#FFFFFF"
            )
            rb.grid(row=i//2, column=i%2, sticky="w", padx=2, pady=2)

        # --- Section 4: Speed Slider ---
        sec4 = tk.LabelFrame(
            self.sidebar, text=" Animation Speed ",
            font=("Segoe UI", 9, "bold"), fg=self.colors["accent"], bg=self.colors["panel_bg"]
        )
        sec4.pack(fill=tk.X, padx=pad_x, pady=pad_y)

        self.speed_slider = tk.Scale(
            sec4, from_=1, to=100, orient=tk.HORIZONTAL,
            bg=self.colors["panel_bg"], fg=self.colors["text"],
            highlightthickness=0, troughcolor="#313244", activebackground="#89B4FA"
        )
        self.speed_slider.set(65)
        self.speed_slider.pack(fill=tk.X, padx=8, pady=(4, 8))

        # --- Section 5: Primary Action Buttons ---
        sec5 = tk.Frame(self.sidebar, bg=self.colors["panel_bg"])
        sec5.pack(fill=tk.X, padx=pad_x, pady=(10, 6))

        self.start_btn = tk.Button(
            sec5, text="▶ START ROBOT SOLVE", font=("Segoe UI", 10, "bold"),
            bg="#A6E3A1", fg="#11111B", activebackground="#94E2D5",
            relief=tk.FLAT, cursor="hand2", pady=5, command=self.start_solve
        )
        self.start_btn.pack(fill=tk.X, pady=(0, 5))

        btn_row = tk.Frame(sec5, bg=self.colors["panel_bg"])
        btn_row.pack(fill=tk.X, pady=(0, 5))

        self.instant_btn = tk.Button(
            btn_row, text="⚡ Instant", font=("Segoe UI", 8, "bold"),
            bg="#F9E2AF", fg="#11111B", relief=tk.FLAT, cursor="hand2",
            command=self.solve_instant
        )
        self.instant_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        self.reset_btn = tk.Button(
            btn_row, text="⏹ Reset", font=("Segoe UI", 8, "bold"),
            bg="#F38BA8", fg="#11111B", relief=tk.FLAT, cursor="hand2",
            command=self.reset_robot_position
        )
        self.reset_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

        btn_row2 = tk.Frame(sec5, bg=self.colors["panel_bg"])
        btn_row2.pack(fill=tk.X, pady=(0, 5))

        clear_p_btn = tk.Button(
            btn_row2, text="🧹 Clear Path", font=("Segoe UI", 8),
            bg="#313244", fg="#CDD6F4", relief=tk.FLAT, cursor="hand2",
            command=self.clear_search_overlay
        )
        clear_p_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))

        clear_w_btn = tk.Button(
            btn_row2, text="🗑 Clear Walls", font=("Segoe UI", 8),
            bg="#313244", fg="#CDD6F4", relief=tk.FLAT, cursor="hand2",
            command=self.clear_all_walls
        )
        clear_w_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

        # Compare All Algorithms Button
        self.compare_btn = tk.Button(
            sec5, text="📊 RUN ALL & COMPARE", font=("Segoe UI", 9, "bold"),
            bg="#CBA6F7", fg="#11111B", activebackground="#B4BEFE",
            relief=tk.FLAT, cursor="hand2", pady=4, command=self.compare_all_algorithms
        )
        self.compare_btn.pack(fill=tk.X, pady=(4, 0))

    def _build_right_panel_widgets(self):
        # Top HUD Dashboard
        self.hud_frame = tk.Frame(self.right_panel, bg=self.colors["panel_bg"], height=70)
        self.hud_frame.pack(fill=tk.X, pady=(0, 10))

        # Metric Tiles inside HUD
        self.metric_tiles = {}
        tile_defs = [
            ("STATUS", "Ready", "#89B4FA"),
            ("EXPLORED", "0 states", "#74C7EC"),
            ("PATH LENGTH", "0 steps", "#F9E2AF"),
            ("SEARCH TIME", "0.00 ms", "#A6E3A1"),
            ("ROBOT STEPS", "0 / 0", "#CBA6F7")
        ]

        for i, (label, default_val, color) in enumerate(tile_defs):
            frame = tk.Frame(self.hud_frame, bg=self.colors["panel_bg"], padx=10, pady=6)
            frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)

            t_lbl = tk.Label(frame, text=label, font=("Segoe UI", 7, "bold"), fg=self.colors["subtext"], bg=self.colors["panel_bg"])
            t_lbl.pack(anchor="w")

            v_lbl = tk.Label(frame, text=default_val, font=("Segoe UI", 12, "bold"), fg=color, bg=self.colors["panel_bg"])
            v_lbl.pack(anchor="w")

            self.metric_tiles[label] = v_lbl

        # Canvas Frame
        self.canvas_frame = tk.Frame(self.right_panel, bg=self.colors["panel_bg"], relief=tk.FLAT)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            self.canvas_frame, bg=self.colors["canvas_bg"],
            highlightthickness=0, cursor="crosshair"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Mouse Event bindings for interactive grid drawing
        self.canvas.bind("<Button-1>", self._on_canvas_left_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_left_drag)
        self.canvas.bind("<Button-3>", self._on_canvas_right_click)
        self.canvas.bind("<B3-Motion>", self._on_canvas_right_drag)
        self.canvas.bind("<Configure>", lambda e: self.draw_maze())

    def _get_algo_desc(self, algo_name):
        descs = {
            "A* Search (Manhattan)": "Optimal & Complete. Combines path cost g(n) with admissible Manhattan distance h(n).",
            "A* Search (Euclidean)": "Optimal & Complete. Uses Euclidean straight-line distance heuristic.",
            "Breadth-First Search (BFS)": "Uninformed & Optimal. Explores shallowest nodes level by level with FIFO queue.",
            "Depth-First Search (DFS)": "Uninformed & Non-Optimal. Traverses deep branches with LIFO stack; may wander.",
            "Greedy Best-First (Manhattan)": "Informed & Fast. Expands strictly by lowest h(n). Can get caught in dead ends.",
            "Uniform Cost Search (UCS)": "Uninformed & Optimal. Expands lowest path cost g(n); Dijkstra equivalent."
        }
        return descs.get(algo_name, "")

    def _on_algo_changed(self, event=None):
        self.algo_desc_lbl.config(text=self._get_algo_desc(self.algo_var.get()))

    # ------------------ Drawing & Rendering ------------------

    def get_cell_metrics(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 100 or h < 100:
            w, h = 760, 680

        cell_w = (w - 20) / self.cols
        cell_h = (h - 20) / self.rows
        cell_size = max(10, min(cell_w, cell_h))

        offset_x = (w - (self.cols * cell_size)) / 2
        offset_y = (h - (self.rows * cell_size)) / 2
        return cell_size, offset_x, offset_y

    def draw_maze(self):
        self.canvas.delete("all")
        cell_size, offset_x, offset_y = self.get_cell_metrics()

        # Render cells
        for r in range(self.rows):
            for c in range(self.cols):
                x1 = offset_x + c * cell_size
                y1 = offset_y + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                cell_val = self.maze.grid[r][c]

                # Default empty background
                fill_color = self.colors["empty"]
                border_color = self.colors["grid_line"]

                if cell_val == WALL:
                    fill_color = self.colors["wall"]
                    border_color = self.colors["wall_border"]
                elif (r, c) == self.maze.start:
                    fill_color = self.colors["start"]
                elif (r, c) == self.maze.goal:
                    fill_color = self.colors["goal"]
                elif (r, c) in self.path_cells:
                    fill_color = self.colors["path"]
                elif (r, c) in self.robot.trail:
                    fill_color = self.colors["trail"]
                elif (r, c) in self.explored_set:
                    fill_color = self.colors["explored_early"]

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fill_color, outline=border_color, width=1,
                    tags=f"cell_{r}_{c}"
                )

                # Start and Goal markers
                if (r, c) == self.maze.start:
                    self.canvas.create_text(
                        (x1 + x2)/2, (y1 + y2)/2, text="S",
                        font=("Segoe UI", max(8, int(cell_size * 0.45)), "bold"),
                        fill="#11111B", tags="marker"
                    )
                elif (r, c) == self.maze.goal:
                    self.canvas.create_text(
                        (x1 + x2)/2, (y1 + y2)/2, text="G",
                        font=("Segoe UI", max(8, int(cell_size * 0.45)), "bold"),
                        fill="#FFFFFF", tags="marker"
                    )

        # Draw path connecting line if path exists
        if len(self.path_cells) > 1 and self.current_result and self.current_result.path:
            path_pts = []
            for (pr, pc) in self.current_result.path:
                px = offset_x + (pc + 0.5) * cell_size
                py = offset_y + (pr + 0.5) * cell_size
                path_pts.extend([px, py])
            if len(path_pts) >= 4:
                self.canvas.create_line(
                    path_pts, fill="#F9E2AF", width=max(2, int(cell_size * 0.2)),
                    capstyle=tk.ROUND, joinstyle=tk.ROUND, tags="path_line"
                )

        # Draw the 2D Robot
        self.canvas.delete("robot")
        self.robot.draw(self.canvas, cell_size, offset_x, offset_y, self.pulse_frame)

    # ------------------ Interactive Grid Controls ------------------

    def _get_coords_from_event(self, event):
        cell_size, offset_x, offset_y = self.get_cell_metrics()
        c = int((event.x - offset_x) // cell_size)
        r = int((event.y - offset_y) // cell_size)
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return r, c
        return None, None

    def _on_canvas_left_click(self, event):
        r, c = self._get_coords_from_event(event)
        if r is None or self.is_searching or self.is_animating_robot:
            return
        
        mode = self.mouse_mode.get()
        if mode == "wall":
            self.maze.set_wall(r, c, is_wall=True)
        elif mode == "erase":
            self.maze.set_wall(r, c, is_wall=False)
        elif mode == "start":
            self.maze.set_start(r, c)
            self.robot.reset(self.maze.start)
        elif mode == "goal":
            self.maze.set_goal(r, c)

        self.clear_search_overlay()
        self.draw_maze()

    def _on_canvas_left_drag(self, event):
        r, c = self._get_coords_from_event(event)
        if r is None or self.is_searching or self.is_animating_robot:
            return

        mode = self.mouse_mode.get()
        if mode == "wall":
            if self.maze.set_wall(r, c, is_wall=True):
                self.draw_maze()
        elif mode == "erase":
            if self.maze.set_wall(r, c, is_wall=False):
                self.draw_maze()

    def _on_canvas_right_click(self, event):
        r, c = self._get_coords_from_event(event)
        if r is not None and not self.is_searching and not self.is_animating_robot:
            self.maze.set_wall(r, c, is_wall=False)
            self.draw_maze()

    def _on_canvas_right_drag(self, event):
        r, c = self._get_coords_from_event(event)
        if r is not None and not self.is_searching and not self.is_animating_robot:
            if self.maze.set_wall(r, c, is_wall=False):
                self.draw_maze()

    # ------------------ Maze Generation ------------------

    def generate_selected_maze(self):
        if self.is_searching or self.is_animating_robot:
            return
        self.clear_search_overlay()
        selection = self.maze_var.get()

        if selection == "Recursive Backtracker":
            self.maze.generate_recursive_backtracker()
        elif selection == "Prim's Algorithm":
            self.maze.generate_prims()
        elif "25%" in selection:
            self.maze.generate_random_obstacles(0.25)
        elif "35%" in selection:
            self.maze.generate_random_obstacles(0.35)
        elif "Bottleneck" in selection:
            self.maze.generate_preset("Bottleneck")
        elif "Spiral" in selection:
            self.maze.generate_preset("Spiral")
        elif "Multi-Room" in selection:
            self.maze.generate_preset("Multi-Room")
        elif "Trap" in selection:
            self.maze.generate_preset("Trap / Local Minima")
        elif selection == "Blank Canvas":
            self.maze.reset_grid()

        self.robot.reset(self.maze.start)
        self.metric_tiles["STATUS"].config(text="Maze Ready", fg="#89B4FA")
        self.draw_maze()

    def clear_search_overlay(self):
        if self.anim_after_id:
            self.root.after_cancel(self.anim_after_id)
            self.anim_after_id = None
        self.is_searching = False
        self.is_animating_robot = False
        self.explored_set.clear()
        self.path_cells.clear()
        self.current_result = None
        self.robot.reset(self.maze.start)
        self.metric_tiles["STATUS"].config(text="Ready", fg="#89B4FA")
        self.metric_tiles["EXPLORED"].config(text="0 states")
        self.metric_tiles["PATH LENGTH"].config(text="0 steps")
        self.metric_tiles["SEARCH TIME"].config(text="0.00 ms")
        self.metric_tiles["ROBOT STEPS"].config(text="0 / 0")
        self.draw_maze()

    def clear_all_walls(self):
        self.clear_search_overlay()
        self.maze.reset_grid()
        self.robot.reset(self.maze.start)
        self.draw_maze()

    def reset_robot_position(self):
        if self.anim_after_id:
            self.root.after_cancel(self.anim_after_id)
            self.anim_after_id = None
        self.is_searching = False
        self.is_animating_robot = False
        self.robot.reset(self.maze.start)
        self.metric_tiles["STATUS"].config(text="Robot Reset", fg="#89B4FA")
        self.draw_maze()

    # ------------------ Search & Robot Animation ------------------

    def start_solve(self):
        if self.is_searching or self.is_animating_robot:
            return

        self.clear_search_overlay()
        algo_name = self.algo_var.get()
        runner = ALGORITHMS.get(algo_name)
        if not runner:
            return

        self.metric_tiles["STATUS"].config(text="Searching...", fg="#F9E2AF")
        self.root.update_idletasks()

        # Run the search algorithm
        result = runner(self.maze)
        self.current_result = result

        # Update HUD Metrics
        self.metric_tiles["SEARCH TIME"].config(text=f"{result.execution_time_ms:.2f} ms")
        self.metric_tiles["EXPLORED"].config(text=f"{result.nodes_explored} states")

        if not result.success:
            self.metric_tiles["STATUS"].config(text="NO PATH FOUND", fg=self.colors["danger"])
            messagebox.showwarning("Search Outcome", f"Goal is completely blocked! No valid path found by {algo_name}.")
            return

        self.metric_tiles["PATH LENGTH"].config(text=f"{result.path_length} steps")
        self.metric_tiles["ROBOT STEPS"].config(text=f"0 / {result.path_length}")

        # Start sequential animation:
        # 1. Search exploration animation
        # 2. Path highlight
        # 3. 2D Robot physical traversal
        self.is_searching = True
        self.anim_step_index = 0
        self._animate_search_expansion()

    def _get_anim_delay(self):
        slider_val = self.speed_slider.get()
        # map 1..100 to delay ms (100 -> 5ms, 1 -> 180ms)
        delay = int(180 - (slider_val / 100.0) * 175)
        return max(3, delay)

    def _animate_search_expansion(self):
        if not self.is_searching or not self.current_result:
            return

        # Animate in batches for high speeds
        slider_val = self.speed_slider.get()
        batch_size = 1 if slider_val < 40 else (2 if slider_val < 70 else 5)

        for _ in range(batch_size):
            if self.anim_step_index < len(self.current_result.explored_order):
                node = self.current_result.explored_order[self.anim_step_index]
                self.explored_set.add(node)
                self.anim_step_index += 1
            else:
                break

        self.draw_maze()

        if self.anim_step_index < len(self.current_result.explored_order):
            self.anim_after_id = self.root.after(self._get_anim_delay(), self._animate_search_expansion)
        else:
            # Exploration finished, reveal path
            self.is_searching = False
            self.path_cells = set(self.current_result.path)
            self.metric_tiles["STATUS"].config(text="Navigating...", fg="#A6E3A1")
            self.draw_maze()
            
            # Start robot movement animation
            self.is_animating_robot = True
            self.robot.set_path(self.current_result.path)
            self.anim_after_id = self.root.after(150, self._animate_robot_traversal)

    def _animate_robot_traversal(self):
        if not self.is_animating_robot or not self.current_result:
            return

        self.pulse_frame += 1
        moved = self.robot.step()
        self.metric_tiles["ROBOT STEPS"].config(
            text=f"{self.robot.steps_taken} / {self.current_result.path_length}"
        )
        self.draw_maze()

        if moved:
            # Robot still moving
            delay = max(25, int(self._get_anim_delay() * 1.5))
            self.anim_after_id = self.root.after(delay, self._animate_robot_traversal)
        else:
            # Robot reached the goal!
            self.is_animating_robot = False
            self.metric_tiles["STATUS"].config(text="GOAL REACHED! 🏆", fg="#00E676")
            self._start_victory_pulse()

    def _start_victory_pulse(self):
        # Pulsing goal animation for celebration
        def pulse(frame=0):
            if frame < 16 and not self.is_searching and not self.is_animating_robot:
                self.pulse_frame = frame
                self.draw_maze()
                self.root.after(80, lambda: pulse(frame + 1))
        pulse(0)

    def solve_instant(self):
        """Immediately solves without visual delay, jumping robot to goal."""
        self.clear_search_overlay()
        algo_name = self.algo_var.get()
        runner = ALGORITHMS.get(algo_name)
        if not runner:
            return

        result = runner(self.maze)
        self.current_result = result
        self.explored_set = set(result.explored_order)
        self.path_cells = set(result.path)

        self.metric_tiles["SEARCH TIME"].config(text=f"{result.execution_time_ms:.2f} ms")
        self.metric_tiles["EXPLORED"].config(text=f"{result.nodes_explored} states")
        
        if result.success:
            self.metric_tiles["STATUS"].config(text="GOAL REACHED! ⚡", fg="#00E676")
            self.metric_tiles["PATH LENGTH"].config(text=f"{result.path_length} steps")
            self.metric_tiles["ROBOT STEPS"].config(text=f"{result.path_length} / {result.path_length}")
            self.robot.set_path(result.path)
            while self.robot.step():
                pass
        else:
            self.metric_tiles["STATUS"].config(text="NO PATH FOUND", fg=self.colors["danger"])

        self.draw_maze()

    # ------------------ Comparison Benchmark ------------------

    def compare_all_algorithms(self):
        """Runs all algorithms on the current maze and displays comparison dialog + charts."""
        self.metric_tiles["STATUS"].config(text="Benchmarking...", fg="#CBA6F7")
        self.root.update_idletasks()

        results = run_all_comparisons(self.maze)
        print_comparison_table(results)

        # Generate comparison chart
        chart_path = "comparison_chart.png"
        generate_comparison_plots(results, save_path=chart_path, show_window=False)

        # Display Comparison Dialog
        self._show_comparison_dialog(results, chart_path)
        self.metric_tiles["STATUS"].config(text="Benchmark Done", fg="#89B4FA")

    def _show_comparison_dialog(self, results, chart_path):
        dlg = tk.Toplevel(self.root)
        dlg.title("Algorithm Comparison Benchmark Results")
        dlg.geometry("780x560")
        dlg.configure(bg="#1E1E2E")
        dlg.transient(self.root)

        title = tk.Label(
            dlg, text="📊 Algorithm Performance Comparison",
            font=("Segoe UI", 14, "bold"), fg="#89B4FA", bg="#1E1E2E"
        )
        title.pack(pady=10)

        # Treeview table
        columns = ("Algorithm", "Success", "Path Length", "Nodes Explored", "Frontier", "Time (ms)")
        tree = ttk.Treeview(dlg, columns=columns, show="headings", height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)
        tree.column("Algorithm", anchor="w", width=220)

        for r in results:
            succ = "YES" if r.success else "NO"
            tree.insert("", tk.END, values=(r.name, succ, r.path_length, r.nodes_explored, r.max_frontier, f"{r.execution_time_ms:.3f}"))

        tree.pack(fill=tk.BOTH, expand=False, padx=16, pady=8)

        # Observation Summary
        obs_text = (
            "Key Observations:\n"
            "• BFS, UCS, and A* always guarantee the mathematical optimal (shortest) path length.\n"
            "• A* (Manhattan) dramatically prunes state exploration compared to uninformed BFS/UCS.\n"
            "• Greedy Best-First searches aggressively towards the goal but can get trapped or yield sub-optimal paths.\n"
            "• DFS explores deeply down first branches, yielding long, twisting paths in labyrinths."
        )
        obs_lbl = tk.Label(
            dlg, text=obs_text, font=("Segoe UI", 9), fg="#BAC2DE", bg="#1E1E2E",
            justify="left", padx=16, pady=8
        )
        obs_lbl.pack(anchor="w")

        btn_row = tk.Frame(dlg, bg="#1E1E2E")
        btn_row.pack(pady=12)

        def open_chart():
            import subprocess
            try:
                os.startfile(chart_path)
            except Exception:
                pass

        chart_btn = tk.Button(
            btn_row, text="📈 Open High-Res Chart (PNG)", font=("Segoe UI", 9, "bold"),
            bg="#89B4FA", fg="#11111B", padx=10, pady=4, relief=tk.FLAT, cursor="hand2",
            command=open_chart
        )
        chart_btn.pack(side=tk.LEFT, padx=6)

        close_btn = tk.Button(
            btn_row, text="Close", font=("Segoe UI", 9),
            bg="#313244", fg="#CDD6F4", padx=10, pady=4, relief=tk.FLAT, cursor="hand2",
            command=dlg.destroy
        )
        close_btn.pack(side=tk.LEFT, padx=6)

    def _launch_fluids_suite(self):
        import subprocess, sys
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fluids_script = os.path.join(base_dir, "fluids", "python", "visualizer.py")
        if os.path.exists(fluids_script):
            subprocess.Popen([sys.executable, fluids_script])


def launch_gui(rows=25, cols=25):
    root = tk.Tk()
    app = MazeRobotApp(root, rows, cols)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()

