"""
Master Unified Application Launcher: AI with Python & Fluids CFD Suite.
Provides a central dashboard with seamless one-click conversion and navigation
between the Smart 2D Maze-Solving Robot and the Laminar Pipe Flow CFD Simulator.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Add project subfolders to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AI_DIR = os.path.join(BASE_DIR, "ai with pythin")
FLUIDS_DIR = os.path.join(BASE_DIR, "fluids", "python")

if AI_DIR not in sys.path:
    sys.path.insert(0, AI_DIR)
if FLUIDS_DIR not in sys.path:
    sys.path.insert(0, FLUIDS_DIR)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Import AI Robot modules
from maze import Maze, WALL, EMPTY, START, GOAL
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

# Import Fluids modules
from pipe_flow_simulation import PipeFlowSimulation


class UnifiedSuiteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Unified AI & Engineering Suite: Maze Robot & Fluids CFD")
        self.root.geometry("1280x860")
        self.root.minsize(1080, 720)
        self.root.configure(bg="#1E1E2E")

        # Color Palette
        self.theme = {
            "bg": "#1E1E2E",
            "panel": "#181825",
            "card": "#252538",
            "border": "#313244",
            "accent": "#89B4FA",
            "accent_green": "#A6E3A1",
            "accent_red": "#F38BA8",
            "accent_yellow": "#F9E2AF",
            "accent_purple": "#CBA6F7",
            "accent_teal": "#94E2D5",
            "text": "#CDD6F4",
            "subtext": "#A6ADC8"
        }

        self.current_tab = "home"
        self._build_header()
        self._build_page_container()

        # Initialize sub-modules
        self._init_ai_module()
        self._init_fluids_module()

        # Start on Home Page
        self.show_page("home")

    # =========================================================================
    # Header & Global Navigation
    # =========================================================================
    def _build_header(self):
        self.header_frame = tk.Frame(self.root, bg=self.theme["panel"], height=64, padx=16, pady=8)
        self.header_frame.pack(fill=tk.X, side=tk.TOP)
        self.header_frame.pack_propagate(False)

        # Logo / Title
        title_box = tk.Frame(self.header_frame, bg=self.theme["panel"])
        title_box.pack(side=tk.LEFT, fill=tk.Y)

        title_lbl = tk.Label(
            title_box, text="⚡ UNIFIED AI & ENGINEERING SUITE",
            font=("Segoe UI", 13, "bold"), fg="#89B4FA", bg=self.theme["panel"]
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            title_box, text="Autonomous Maze Robot & Laminar Pipe Flow CFD",
            font=("Segoe UI", 8), fg=self.theme["subtext"], bg=self.theme["panel"]
        )
        subtitle_lbl.pack(anchor="w")

        # Conversion / Quick Switch Button (Prominent Center-Right)
        self.convert_btn = tk.Button(
            self.header_frame, text="🔀 SWITCH: AI with Python ➔ Fluids",
            font=("Segoe UI", 10, "bold"), bg="#CBA6F7", fg="#11111B",
            activebackground="#B4BEFE", activeforeground="#11111B",
            relief=tk.FLAT, cursor="hand2", padx=14, pady=5,
            command=self.toggle_conversion
        )
        self.convert_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # Navigation Tabs
        nav_box = tk.Frame(self.header_frame, bg=self.theme["panel"])
        nav_box.pack(side=tk.RIGHT, padx=10)

        self.nav_btns = {}
        tabs = [
            ("home", "🏠 Main Hub"),
            ("ai", "🤖 AI with Python (Maze Robot)"),
            ("fluids", "🌊 Fluids (Pipe Flow CFD)")
        ]
        for key, label in tabs:
            btn = tk.Button(
                nav_box, text=label, font=("Segoe UI", 9, "bold"),
                bg="#313244", fg=self.theme["text"],
                activebackground="#45475A", activeforeground="#FFFFFF",
                relief=tk.FLAT, cursor="hand2", padx=10, pady=5,
                command=lambda k=key: self.show_page(k)
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.nav_btns[key] = btn

    def _build_page_container(self):
        self.pages_container = tk.Frame(self.root, bg=self.theme["bg"])
        self.pages_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Pages
        self.page_home = tk.Frame(self.pages_container, bg=self.theme["bg"])
        self.page_ai = tk.Frame(self.pages_container, bg=self.theme["bg"])
        self.page_fluids = tk.Frame(self.pages_container, bg=self.theme["bg"])

        for p in (self.page_home, self.page_ai, self.page_fluids):
            p.place(x=0, y=0, relwidth=1, relheight=1)

        self._build_home_page()

    def show_page(self, page_key):
        self.current_tab = page_key

        # Update Nav Button Highlights
        for k, btn in self.nav_btns.items():
            if k == page_key:
                btn.config(bg="#89B4FA", fg="#11111B")
            else:
                btn.config(bg="#313244", fg=self.theme["text"])

        # Update Converter Button Text
        if page_key == "ai":
            self.convert_btn.config(
                text="🔀 Switch from AI to Fluids (CFD) ➔",
                bg="#94E2D5", fg="#11111B"
            )
        elif page_key == "fluids":
            self.convert_btn.config(
                text="🔀 Switch from Fluids to AI (Maze) ➔",
                bg="#A6E3A1", fg="#11111B"
            )
        else:
            self.convert_btn.config(
                text="🔀 Convert: AI with Python ➔ Fluids",
                bg="#CBA6F7", fg="#11111B"
            )

        # Bring Selected Page to Front
        if page_key == "home":
            self.page_home.lift()
        elif page_key == "ai":
            self.page_ai.lift()
            self.ai_draw_maze()
        elif page_key == "fluids":
            self.page_fluids.lift()

    def toggle_conversion(self):
        """Toggles directly between AI with Python and Fluids."""
        if self.current_tab == "ai":
            self.show_page("fluids")
        else:
            self.show_page("ai")

    # =========================================================================
    # Page 1: Main Hub / Landing Dashboard
    # =========================================================================
    def _build_home_page(self):
        # Hero Banner
        banner = tk.Frame(self.page_home, bg=self.theme["panel"], padx=25, pady=20)
        banner.pack(fill=tk.X, pady=(0, 16))

        tk.Label(
            banner, text="WELCOME TO THE UNIFIED COMPUTATIONAL LAB",
            font=("Segoe UI", 16, "bold"), fg="#89B4FA", bg=self.theme["panel"]
        ) .pack(anchor="w")

        tk.Label(
            banner,
            text="Seamlessly switch between AI Search Algorithms for autonomous robotics and Computational Fluid Dynamics (CFD) for internal pipe flow.",
            font=("Segoe UI", 10), fg=self.theme["subtext"], bg=self.theme["panel"], pady=4
        ).pack(anchor="w")

        # Two Main Feature Cards (Side by Side)
        cards_frame = tk.Frame(self.page_home, bg=self.theme["bg"])
        cards_frame.pack(fill=tk.BOTH, expand=True)

        # Card 1: AI with Python (Smart Maze Robot)
        c1 = tk.Frame(cards_frame, bg=self.theme["card"], bd=1, relief=tk.SOLID, padx=20, pady=18)
        c1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        badge1 = tk.Label(c1, text=" ARTIFICIAL INTELLIGENCE ", font=("Segoe UI", 8, "bold"), bg="#A6E3A1", fg="#11111B", padx=6, pady=2)
        badge1.pack(anchor="w", pady=(0, 8))

        tk.Label(c1, text="🤖 Smart Maze-Solving Robot", font=("Segoe UI", 15, "bold"), fg="#CDD6F4", bg=self.theme["card"]).pack(anchor="w")
        desc1 = (
            "An autonomous 2D robot navigating procedurally generated mazes using 6 AI search algorithms:\n\n"
            "• Breadth-First Search (BFS) [Optimal]\n"
            "• Depth-First Search (DFS) [Deep Explorer]\n"
            "• Uniform Cost Search (UCS / Dijkstra)\n"
            "• A* Search (Manhattan Heuristic) [Optimal]\n"
            "• A* Search (Euclidean Heuristic) [Optimal]\n"
            "• Greedy Best-First Search [Fast Heuristic]\n\n"
            "Features full real-time animation: state expansion wave, path lighting, rotating chassis, directional headlights, and comparative benchmark graphs."
        )
        tk.Label(c1, text=desc1, font=("Segoe UI", 9), fg=self.theme["subtext"], bg=self.theme["card"], justify="left", wraplength=460).pack(anchor="w", pady=(10, 15))

        btn_ai_launch = tk.Button(
            c1, text="▶ LAUNCH AI MAZE SOLVER", font=("Segoe UI", 11, "bold"),
            bg="#A6E3A1", fg="#11111B", activebackground="#94E2D5",
            relief=tk.FLAT, cursor="hand2", padx=16, pady=8,
            command=lambda: self.show_page("ai")
        )
        btn_ai_launch.pack(fill=tk.X, side=tk.BOTTOM)

        # Card 2: Fluids (Laminar Pipe Flow CFD)
        c2 = tk.Frame(cards_frame, bg=self.theme["card"], bd=1, relief=tk.SOLID, padx=20, pady=18)
        c2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        badge2 = tk.Label(c2, text=" COMPUTATIONAL FLUID DYNAMICS ", font=("Segoe UI", 8, "bold"), bg="#89B4FA", fg="#11111B", padx=6, pady=2)
        badge2.pack(anchor="w", pady=(0, 8))

        tk.Label(c2, text="🌊 Laminar Pipe Flow Simulation", font=("Segoe UI", 15, "bold"), fg="#CDD6F4", bg=self.theme["card"]).pack(anchor="w")
        desc2 = (
            "Numerical simulation of water flow through a circular pipe from inlet to fully developed flow:\n\n"
            "• Inlet Velocity U_in: Configured to student roll number (e.g. 67 m/s)\n"
            "• Laminar Diameter: Auto-calculated for Re = 1600 (D = 23.97 µm)\n"
            "• Entrance Length Le: 2.21 mm (captures developing boundary layer)\n"
            "• Total Pipe Length L: 3.53 mm (shows developed Poiseuille flow)\n"
            "• Accuracy: 99.92% match with Hagen-Poiseuille asymptote\n\n"
            "Complete integration with Python (2D Axisymmetric NS Solver), ANSYS Fluent scripts, and COMSOL Multiphysics models."
        )
        tk.Label(c2, text=desc2, font=("Segoe UI", 9), fg=self.theme["subtext"], bg=self.theme["card"], justify="left", wraplength=460).pack(anchor="w", pady=(10, 15))

        btn_fluids_launch = tk.Button(
            c2, text="🌊 LAUNCH FLUIDS CFD SIMULATOR", font=("Segoe UI", 11, "bold"),
            bg="#89B4FA", fg="#11111B", activebackground="#74C7EC",
            relief=tk.FLAT, cursor="hand2", padx=16, pady=8,
            command=lambda: self.show_page("fluids")
        )
        btn_fluids_launch.pack(fill=tk.X, side=tk.BOTTOM)

    # =========================================================================
    # Page 2: AI with Python (Smart Maze Robot View)
    # =========================================================================
    def _init_ai_module(self):
        self.rows = 25
        self.cols = 25
        self.maze = Maze(self.rows, self.cols)
        self.robot = Robot(self.maze.start)

        self.ai_is_searching = False
        self.ai_is_animating_robot = False
        self.ai_anim_after_id = None
        self.ai_pulse_frame = 0
        self.ai_current_result = None
        self.ai_explored_set = set()
        self.ai_path_cells = set()
        self.ai_anim_step_index = 0
        self.ai_mouse_mode = tk.StringVar(value="wall")

        # Top Bar with Switcher Button
        top_bar = tk.Frame(self.page_ai, bg=self.theme["panel"], padx=12, pady=6)
        top_bar.pack(fill=tk.X, pady=(0, 8))

        lbl = tk.Label(top_bar, text="🤖 AI MAZE-SOLVING ROBOT", font=("Segoe UI", 12, "bold"), fg="#A6E3A1", bg=self.theme["panel"])
        lbl.pack(side=tk.LEFT)

        # Quick Switcher Button inside the page
        switch_to_fluids = tk.Button(
            top_bar, text="🌊 Switch to Fluids (Pipe Flow CFD) ➔",
            font=("Segoe UI", 9, "bold"), bg="#89B4FA", fg="#11111B",
            relief=tk.FLAT, cursor="hand2", padx=12, pady=4,
            command=lambda: self.show_page("fluids")
        )
        switch_to_fluids.pack(side=tk.RIGHT)

        # Main AI Workspace (Left Controls, Right Canvas & HUD)
        ai_body = tk.Frame(self.page_ai, bg=self.theme["bg"])
        ai_body.pack(fill=tk.BOTH, expand=True)

        # Left Sidebar (Controls)
        ai_sidebar = tk.Frame(ai_body, bg=self.theme["panel"], width=310, padx=10, pady=8)
        ai_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        ai_sidebar.pack_propagate(False)

        # Section: Algorithm
        s1 = tk.LabelFrame(ai_sidebar, text=" AI Algorithm ", font=("Segoe UI", 9, "bold"), fg="#89B4FA", bg=self.theme["panel"], padx=6, pady=4)
        s1.pack(fill=tk.X, pady=(0, 6))

        self.ai_algo_var = tk.StringVar(value="A* Search (Manhattan)")
        self.ai_algo_dropdown = ttk.Combobox(
            s1, textvariable=self.ai_algo_var, state="readonly",
            values=list(ALGORITHMS.keys()), font=("Segoe UI", 9)
        )
        self.ai_algo_dropdown.pack(fill=tk.X, pady=4)

        # Section: Maze Generation
        s2 = tk.LabelFrame(ai_sidebar, text=" Maze Environment ", font=("Segoe UI", 9, "bold"), fg="#89B4FA", bg=self.theme["panel"], padx=6, pady=4)
        s2.pack(fill=tk.X, pady=(0, 6))

        self.ai_maze_var = tk.StringVar(value="Recursive Backtracker")
        m_opts = ["Recursive Backtracker", "Prim's Algorithm", "Random Obstacles (25%)", "Random Obstacles (35%)",
                  "Preset: Bottleneck", "Preset: Spiral", "Preset: Multi-Room", "Preset: Trap / Local Minima", "Blank Canvas"]
        self.ai_maze_dropdown = ttk.Combobox(s2, textvariable=self.ai_maze_var, state="readonly", values=m_opts, font=("Segoe UI", 8))
        self.ai_maze_dropdown.pack(fill=tk.X, pady=2)

        gen_btn = tk.Button(s2, text="🎲 Generate Maze", font=("Segoe UI", 8, "bold"), bg="#313244", fg="#CDD6F4", relief=tk.FLAT, cursor="hand2", command=self.ai_generate_maze)
        gen_btn.pack(fill=tk.X, pady=4)

        # Section: Tool Mode
        s3 = tk.LabelFrame(ai_sidebar, text=" Grid Edit Mode ", font=("Segoe UI", 8, "bold"), fg="#89B4FA", bg=self.theme["panel"], padx=4, pady=2)
        s3.pack(fill=tk.X, pady=(0, 6))
        mf = tk.Frame(s3, bg=self.theme["panel"])
        mf.pack(fill=tk.X)
        for i, (txt, val) in enumerate([("Draw Wall", "wall"), ("Erase", "erase"), ("Set Start", "start"), ("Set Goal", "goal")]):
            tk.Radiobutton(mf, text=txt, variable=self.ai_mouse_mode, value=val, font=("Segoe UI", 8), fg="#CDD6F4", bg=self.theme["panel"], selectcolor="#313244").grid(row=i//2, column=i%2, sticky="w")

        # Section: Speed
        s4 = tk.LabelFrame(ai_sidebar, text=" Speed Slider ", font=("Segoe UI", 8, "bold"), fg="#89B4FA", bg=self.theme["panel"], padx=4, pady=2)
        s4.pack(fill=tk.X, pady=(0, 6))
        self.ai_speed_slider = tk.Scale(s4, from_=1, to=100, orient=tk.HORIZONTAL, bg=self.theme["panel"], fg="#CDD6F4", highlightthickness=0, troughcolor="#313244")
        self.ai_speed_slider.set(65)
        self.ai_speed_slider.pack(fill=tk.X)

        # Action Buttons
        s5 = tk.Frame(ai_sidebar, bg=self.theme["panel"])
        s5.pack(fill=tk.X, pady=(6, 0))

        start_btn = tk.Button(s5, text="▶ START ROBOT SOLVE", font=("Segoe UI", 10, "bold"), bg="#A6E3A1", fg="#11111B", relief=tk.FLAT, cursor="hand2", pady=5, command=self.ai_start_solve)
        start_btn.pack(fill=tk.X, pady=(0, 4))

        b_row = tk.Frame(s5, bg=self.theme["panel"])
        b_row.pack(fill=tk.X, pady=(0, 4))
        tk.Button(b_row, text="⚡ Instant", font=("Segoe UI", 8, "bold"), bg="#F9E2AF", fg="#11111B", relief=tk.FLAT, cursor="hand2", command=self.ai_solve_instant).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        tk.Button(b_row, text="⏹ Reset", font=("Segoe UI", 8, "bold"), bg="#F38BA8", fg="#11111B", relief=tk.FLAT, cursor="hand2", command=self.ai_reset_robot).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

        b_row2 = tk.Frame(s5, bg=self.theme["panel"])
        b_row2.pack(fill=tk.X, pady=(0, 4))
        tk.Button(b_row2, text="🧹 Clear Path", font=("Segoe UI", 8), bg="#313244", fg="#CDD6F4", relief=tk.FLAT, cursor="hand2", command=self.ai_clear_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        tk.Button(b_row2, text="🗑 Clear Walls", font=("Segoe UI", 8), bg="#313244", fg="#CDD6F4", relief=tk.FLAT, cursor="hand2", command=self.ai_clear_walls).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))

        compare_btn = tk.Button(s5, text="📊 RUN ALL & COMPARE", font=("Segoe UI", 9, "bold"), bg="#CBA6F7", fg="#11111B", relief=tk.FLAT, cursor="hand2", pady=4, command=self.ai_compare_all)
        compare_btn.pack(fill=tk.X, pady=(4, 0))

        # Right Area: Top HUD + Canvas
        ai_main = tk.Frame(ai_body, bg=self.theme["bg"])
        ai_main.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        hud = tk.Frame(ai_main, bg=self.theme["panel"], height=55)
        hud.pack(fill=tk.X, pady=(0, 6))

        self.ai_tiles = {}
        for label, def_val, col in [("STATUS", "Ready", "#89B4FA"), ("EXPLORED", "0 states", "#74C7EC"),
                                    ("PATH LENGTH", "0 steps", "#F9E2AF"), ("SEARCH TIME", "0.00 ms", "#A6E3A1"),
                                    ("ROBOT PROGRESS", "0 / 0", "#CBA6F7")]:
            f = tk.Frame(hud, bg=self.theme["panel"], padx=10, pady=4)
            f.pack(side=tk.LEFT, fill=tk.Y, expand=True)
            tk.Label(f, text=label, font=("Segoe UI", 7, "bold"), fg=self.theme["subtext"], bg=self.theme["panel"]).pack(anchor="w")
            v_lbl = tk.Label(f, text=def_val, font=("Segoe UI", 11, "bold"), fg=col, bg=self.theme["panel"])
            v_lbl.pack(anchor="w")
            self.ai_tiles[label] = v_lbl

        # Canvas
        self.ai_canvas = tk.Canvas(ai_main, bg="#11111B", highlightthickness=0, cursor="crosshair")
        self.ai_canvas.pack(fill=tk.BOTH, expand=True)

        # Mouse Bindings
        self.ai_canvas.bind("<Button-1>", self.ai_click)
        self.ai_canvas.bind("<B1-Motion>", self.ai_drag)
        self.ai_canvas.bind("<Button-3>", self.ai_rclick)
        self.ai_canvas.bind("<B3-Motion>", self.ai_rdrag)
        self.ai_canvas.bind("<Configure>", lambda e: self.ai_draw_maze())

        self.maze.generate_recursive_backtracker()
        self.robot.reset(self.maze.start)

    def ai_get_cell_metrics(self):
        w = self.ai_canvas.winfo_width()
        h = self.ai_canvas.winfo_height()
        if w < 100 or h < 100:
            w, h = 760, 600
        cs = max(8, min((w - 20) / self.cols, (h - 20) / self.rows))
        ox = (w - self.cols * cs) / 2
        oy = (h - self.rows * cs) / 2
        return cs, ox, oy

    def ai_draw_maze(self):
        self.ai_canvas.delete("all")
        cs, ox, oy = self.ai_get_cell_metrics()

        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = ox + c * cs, oy + r * cs
                x2, y2 = x1 + cs, y1 + cs
                val = self.maze.grid[r][c]

                fill = "#1E1E2E"
                outline = "#232336"
                if val == WALL:
                    fill = "#45475A"
                    outline = "#585B70"
                elif (r, c) == self.maze.start:
                    fill = "#A6E3A1"
                elif (r, c) == self.maze.goal:
                    fill = "#F38BA8"
                elif (r, c) in self.ai_path_cells:
                    fill = "#F9E2AF"
                elif (r, c) in self.robot.trail:
                    fill = "#EBA0AC"
                elif (r, c) in self.ai_explored_set:
                    fill = "#74C7EC"

                self.ai_canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=1)
                if (r, c) == self.maze.start:
                    self.ai_canvas.create_text((x1+x2)/2, (y1+y2)/2, text="S", font=("Segoe UI", max(8, int(cs*0.45)), "bold"), fill="#11111B")
                elif (r, c) == self.maze.goal:
                    self.ai_canvas.create_text((x1+x2)/2, (y1+y2)/2, text="G", font=("Segoe UI", max(8, int(cs*0.45)), "bold"), fill="#FFFFFF")

        # Path Line
        if len(self.ai_path_cells) > 1 and self.ai_current_result and self.ai_current_result.path:
            pts = []
            for pr, pc in self.ai_current_result.path:
                pts.extend([ox + (pc + 0.5) * cs, oy + (pr + 0.5) * cs])
            if len(pts) >= 4:
                self.ai_canvas.create_line(pts, fill="#F9E2AF", width=max(2, int(cs * 0.2)), capstyle=tk.ROUND, joinstyle=tk.ROUND)

        # Robot
        self.ai_canvas.delete("robot")
        self.robot.draw(self.ai_canvas, cs, ox, oy, self.ai_pulse_frame)

    def ai_click(self, event):
        cs, ox, oy = self.ai_get_cell_metrics()
        c = int((event.x - ox) // cs)
        r = int((event.y - oy) // cs)
        if 0 <= r < self.rows and 0 <= c < self.cols:
            mode = self.ai_mouse_mode.get()
            if mode == "wall": self.maze.set_wall(r, c, True)
            elif mode == "erase": self.maze.set_wall(r, c, False)
            elif mode == "start": self.maze.set_start(r, c); self.robot.reset(self.maze.start)
            elif mode == "goal": self.maze.set_goal(r, c)
            self.ai_clear_path()
            self.ai_draw_maze()

    def ai_drag(self, event):
        cs, ox, oy = self.ai_get_cell_metrics()
        c = int((event.x - ox) // cs)
        r = int((event.y - oy) // cs)
        if 0 <= r < self.rows and 0 <= c < self.cols:
            mode = self.ai_mouse_mode.get()
            if mode == "wall" and self.maze.set_wall(r, c, True): self.ai_draw_maze()
            elif mode == "erase" and self.maze.set_wall(r, c, False): self.ai_draw_maze()

    def ai_rclick(self, event):
        cs, ox, oy = self.ai_get_cell_metrics()
        c = int((event.x - ox) // cs)
        r = int((event.y - oy) // cs)
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.maze.set_wall(r, c, False)
            self.ai_draw_maze()

    def ai_rdrag(self, event):
        self.ai_rclick(event)

    def ai_generate_maze(self):
        self.ai_clear_path()
        sel = self.ai_maze_var.get()
        if sel == "Recursive Backtracker": self.maze.generate_recursive_backtracker()
        elif sel == "Prim's Algorithm": self.maze.generate_prims()
        elif "25%" in sel: self.maze.generate_random_obstacles(0.25)
        elif "35%" in sel: self.maze.generate_random_obstacles(0.35)
        elif "Bottleneck" in sel: self.maze.generate_preset("Bottleneck")
        elif "Spiral" in sel: self.maze.generate_preset("Spiral")
        elif "Multi-Room" in sel: self.maze.generate_preset("Multi-Room")
        elif "Trap" in sel: self.maze.generate_preset("Trap / Local Minima")
        elif sel == "Blank Canvas": self.maze.reset_grid()
        self.robot.reset(self.maze.start)
        self.ai_tiles["STATUS"].config(text="Maze Ready", fg="#89B4FA")
        self.ai_draw_maze()

    def ai_clear_path(self):
        if self.ai_anim_after_id:
            self.root.after_cancel(self.ai_anim_after_id)
            self.ai_anim_after_id = None
        self.ai_is_searching = False
        self.ai_is_animating_robot = False
        self.ai_explored_set.clear()
        self.ai_path_cells.clear()
        self.ai_current_result = None
        self.robot.reset(self.maze.start)
        self.ai_tiles["STATUS"].config(text="Ready", fg="#89B4FA")
        self.ai_tiles["EXPLORED"].config(text="0 states")
        self.ai_tiles["PATH LENGTH"].config(text="0 steps")
        self.ai_tiles["SEARCH TIME"].config(text="0.00 ms")
        self.ai_tiles["ROBOT PROGRESS"].config(text="0 / 0")
        self.ai_draw_maze()

    def ai_clear_walls(self):
        self.ai_clear_path()
        self.maze.reset_grid()
        self.robot.reset(self.maze.start)
        self.ai_draw_maze()

    def ai_reset_robot(self):
        if self.ai_anim_after_id:
            self.root.after_cancel(self.ai_anim_after_id)
            self.ai_anim_after_id = None
        self.ai_is_searching = False
        self.ai_is_animating_robot = False
        self.robot.reset(self.maze.start)
        self.ai_tiles["STATUS"].config(text="Robot Reset", fg="#89B4FA")
        self.ai_draw_maze()

    def ai_start_solve(self):
        if self.ai_is_searching or self.ai_is_animating_robot:
            return
        self.ai_clear_path()
        name = self.ai_algo_var.get()
        runner = ALGORITHMS.get(name)
        if not runner: return

        self.ai_tiles["STATUS"].config(text="Searching...", fg="#F9E2AF")
        self.root.update_idletasks()

        res = runner(self.maze)
        self.ai_current_result = res
        self.ai_tiles["SEARCH TIME"].config(text=f"{res.execution_time_ms:.2f} ms")
        self.ai_tiles["EXPLORED"].config(text=f"{res.nodes_explored} states")

        if not res.success:
            self.ai_tiles["STATUS"].config(text="NO PATH", fg="#F38BA8")
            messagebox.showwarning("Search Result", "No valid path found (Goal is completely walled off)!")
            return

        self.ai_tiles["PATH LENGTH"].config(text=f"{res.path_length} steps")
        self.ai_tiles["ROBOT PROGRESS"].config(text=f"0 / {res.path_length}")

        self.ai_is_searching = True
        self.ai_anim_step_index = 0
        self._ai_step_search()

    def _ai_step_search(self):
        if not self.ai_is_searching or not self.ai_current_result: return
        val = self.ai_speed_slider.get()
        batch = 1 if val < 40 else (2 if val < 70 else 5)
        for _ in range(batch):
            if self.ai_anim_step_index < len(self.ai_current_result.explored_order):
                self.ai_explored_set.add(self.ai_current_result.explored_order[self.ai_anim_step_index])
                self.ai_anim_step_index += 1
            else: break
        self.ai_draw_maze()

        if self.ai_anim_step_index < len(self.ai_current_result.explored_order):
            delay = max(3, int(180 - (val / 100.0) * 175))
            self.ai_anim_after_id = self.root.after(delay, self._ai_step_search)
        else:
            self.ai_is_searching = False
            self.ai_path_cells = set(self.ai_current_result.path)
            self.ai_tiles["STATUS"].config(text="Navigating...", fg="#A6E3A1")
            self.ai_draw_maze()
            self.ai_is_animating_robot = True
            self.robot.set_path(self.ai_current_result.path)
            self.ai_anim_after_id = self.root.after(150, self._ai_step_robot)

    def _ai_step_robot(self):
        if not self.ai_is_animating_robot or not self.ai_current_result: return
        self.ai_pulse_frame += 1
        moved = self.robot.step()
        self.ai_tiles["ROBOT PROGRESS"].config(text=f"{self.robot.steps_taken} / {self.ai_current_result.path_length}")
        self.ai_draw_maze()
        if moved:
            val = self.ai_speed_slider.get()
            delay = max(25, int((180 - (val / 100.0) * 175) * 1.5))
            self.ai_anim_after_id = self.root.after(delay, self._ai_step_robot)
        else:
            self.ai_is_animating_robot = False
            self.ai_tiles["STATUS"].config(text="GOAL REACHED! 🏆", fg="#00E676")

    def ai_solve_instant(self):
        self.ai_clear_path()
        name = self.ai_algo_var.get()
        runner = ALGORITHMS.get(name)
        if not runner: return
        res = runner(self.maze)
        self.ai_current_result = res
        self.ai_explored_set = set(res.explored_order)
        self.ai_path_cells = set(res.path)
        self.ai_tiles["SEARCH TIME"].config(text=f"{res.execution_time_ms:.2f} ms")
        self.ai_tiles["EXPLORED"].config(text=f"{res.nodes_explored} states")
        if res.success:
            self.ai_tiles["STATUS"].config(text="GOAL REACHED! ⚡", fg="#00E676")
            self.ai_tiles["PATH LENGTH"].config(text=f"{res.path_length} steps")
            self.ai_tiles["ROBOT PROGRESS"].config(text=f"{res.path_length} / {res.path_length}")
            self.robot.set_path(res.path)
            while self.robot.step(): pass
        self.ai_draw_maze()

    def ai_compare_all(self):
        self.ai_tiles["STATUS"].config(text="Benchmarking...", fg="#CBA6F7")
        self.root.update_idletasks()
        results = run_all_comparisons(self.maze)
        print_comparison_table(results)
        generate_comparison_plots(results, "comparison_chart.png", False)

        dlg = tk.Toplevel(self.root)
        dlg.title("Algorithm Comparison Benchmark")
        dlg.geometry("740x500")
        dlg.configure(bg="#1E1E2E")
        tk.Label(dlg, text="📊 Benchmark Comparison on Current Maze", font=("Segoe UI", 13, "bold"), fg="#89B4FA", bg="#1E1E2E").pack(pady=10)

        tree = ttk.Treeview(dlg, columns=("Algorithm", "Success", "Path (Steps)", "Explored", "Frontier", "Time (ms)"), show="headings", height=8)
        for c in ("Algorithm", "Success", "Path (Steps)", "Explored", "Frontier", "Time (ms)"):
            tree.heading(c, text=c)
            tree.column(c, anchor="center", width=110)
        tree.column("Algorithm", anchor="w", width=200)
        for r in results:
            tree.insert("", tk.END, values=(r.name, "YES" if r.success else "NO", r.path_length, r.nodes_explored, r.max_frontier, f"{r.execution_time_ms:.3f}"))
        tree.pack(fill=tk.BOTH, expand=False, padx=16, pady=8)

        tk.Label(dlg, text="• BFS, UCS, and A* guarantee mathematical optimal path length.\n• A* prunes nodes drastically via admissible heuristics.\n• DFS can wander along twisting sub-optimal branches.",
                 font=("Segoe UI", 9), fg="#BAC2DE", bg="#1E1E2E", justify="left").pack(anchor="w", padx=16, pady=8)

        tk.Button(dlg, text="Open High-Res Chart (PNG)", font=("Segoe UI", 9, "bold"), bg="#89B4FA", fg="#11111B", padx=10, pady=4, relief=tk.FLAT,
                  command=lambda: os.startfile("comparison_chart.png") if hasattr(os, "startfile") else None).pack(pady=6)
        self.ai_tiles["STATUS"].config(text="Benchmark Done", fg="#89B4FA")

    # =========================================================================
    # Page 3: Fluids (Laminar Pipe Flow CFD View)
    # =========================================================================
    def _init_fluids_module(self):
        # Top Bar with Switcher Button
        top_bar = tk.Frame(self.page_fluids, bg=self.theme["panel"], padx=12, pady=6)
        top_bar.pack(fill=tk.X, pady=(0, 8))

        lbl = tk.Label(top_bar, text="🌊 LAMINAR PIPE FLOW CFD SIMULATION", font=("Segoe UI", 12, "bold"), fg="#89B4FA", bg=self.theme["panel"])
        lbl.pack(side=tk.LEFT)

        switch_to_ai = tk.Button(
            top_bar, text="🤖 Switch to AI with Python (Maze Robot) ➔",
            font=("Segoe UI", 9, "bold"), bg="#A6E3A1", fg="#11111B",
            relief=tk.FLAT, cursor="hand2", padx=12, pady=4,
            command=lambda: self.show_page("ai")
        )
        switch_to_ai.pack(side=tk.RIGHT)

        # Fluids Body: Left Parameter Controls, Right Matplotlib Notebook Tabs
        f_body = tk.Frame(self.page_fluids, bg=self.theme["bg"])
        f_body.pack(fill=tk.BOTH, expand=True)

        # Left Controls
        f_side = tk.Frame(f_body, bg=self.theme["panel"], width=310, padx=10, pady=10)
        f_side.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
        f_side.pack_propagate(False)

        p_grp = tk.LabelFrame(f_side, text=" Simulation Parameters ", font=("Segoe UI", 9, "bold"), fg="#89B4FA", bg=self.theme["panel"], padx=6, pady=6)
        p_grp.pack(fill=tk.X, pady=(0, 8))

        tk.Label(p_grp, text="Roll Number (Last 2 digits = U_in m/s):", font=("Segoe UI", 8), fg="#CDD6F4", bg=self.theme["panel"]).pack(anchor="w")
        self.f_roll_var = tk.StringVar(value="67")
        tk.Entry(p_grp, textvariable=self.f_roll_var, font=("Segoe UI", 9), bg="#313244", fg="#FFFFFF").pack(fill=tk.X, pady=(2, 6))

        tk.Label(p_grp, text="Target Reynolds Number (< 2300):", font=("Segoe UI", 8), fg="#CDD6F4", bg=self.theme["panel"]).pack(anchor="w")
        self.f_re_var = tk.StringVar(value="1600")
        tk.Entry(p_grp, textvariable=self.f_re_var, font=("Segoe UI", 9), bg="#313244", fg="#FFFFFF").pack(fill=tk.X, pady=(2, 6))

        tk.Label(p_grp, text="Radial Grid Points (Nr):", font=("Segoe UI", 8), fg="#CDD6F4", bg=self.theme["panel"]).pack(anchor="w")
        self.f_nr_var = tk.StringVar(value="80")
        tk.Entry(p_grp, textvariable=self.f_nr_var, font=("Segoe UI", 9), bg="#313244", fg="#FFFFFF").pack(fill=tk.X, pady=(2, 6))

        tk.Label(p_grp, text="Axial Grid Stations (Nx):", font=("Segoe UI", 8), fg="#CDD6F4", bg=self.theme["panel"]).pack(anchor="w")
        self.f_nx_var = tk.StringVar(value="300")
        tk.Entry(p_grp, textvariable=self.f_nx_var, font=("Segoe UI", 9), bg="#313244", fg="#FFFFFF").pack(fill=tk.X, pady=(2, 8))

        f_run_btn = tk.Button(f_side, text="🚀 RUN CFD SIMULATION", font=("Segoe UI", 10, "bold"), bg="#89B4FA", fg="#11111B", relief=tk.FLAT, cursor="hand2", pady=6, command=self.fluids_run_sim)
        f_run_btn.pack(fill=tk.X, pady=(0, 10))

        # Hydrodynamic Summary Box
        h_grp = tk.LabelFrame(f_side, text=" Calculated Hydrodynamics ", font=("Segoe UI", 9, "bold"), fg="#89B4FA", bg=self.theme["panel"], padx=6, pady=6)
        h_grp.pack(fill=tk.BOTH, expand=True)

        self.f_summary_txt = tk.Text(h_grp, font=("Consolas", 8), bg=self.theme["panel"], fg="#CDD6F4", wrap=tk.WORD, relief=tk.FLAT, highlightthickness=0)
        self.f_summary_txt.pack(fill=tk.BOTH, expand=True)

        # Right Tabbed Display
        f_main = tk.Frame(f_body, bg=self.theme["panel"])
        f_main.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.f_notebook = ttk.Notebook(f_main)
        self.f_notebook.pack(fill=tk.BOTH, expand=True)

        self.f_tab1 = tk.Frame(self.f_notebook, bg="#181825")
        self.f_tab2 = tk.Frame(self.f_notebook, bg="#181825")
        self.f_tab3 = tk.Frame(self.f_notebook, bg="#181825")
        self.f_tab4 = tk.Frame(self.f_notebook, bg="#181825")

        self.f_notebook.add(self.f_tab1, text="2D Velocity Contour")
        self.f_notebook.add(self.f_tab2, text="Radial Profiles")
        self.f_notebook.add(self.f_tab3, text="Centerline uc(x)")
        self.f_notebook.add(self.f_tab4, text="Pressure Drop")

        # Initial Run
        self.fluids_run_sim()

    def fluids_run_sim(self):
        try:
            roll = int(self.f_roll_var.get())
            re = float(self.f_re_var.get())
            nr = int(self.f_nr_var.get())
            nx = int(self.f_nx_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric parameters for fluids simulation.")
            return

        self.f_sim = PipeFlowSimulation(roll_number=roll, target_re=re, nr=nr, nx=nx)
        self.f_sim.solve()

        # Update Summary
        s = self.f_sim.summary()
        self.f_summary_txt.delete("1.0", tk.END)
        lines = [
            f"• Inlet Vel U_in : {s['Inlet Velocity U_in (m/s)']:.1f} m/s",
            f"• Reynolds Re    : {s['Target Reynolds Number Re']:.0f} (Laminar)",
            f"• Fluid          : Water (20°C)",
            f"• Density rho    : {s['Density (kg/m3)']:.1f} kg/m³",
            f"• Viscosity mu   : {s['Dynamic Viscosity (Pa.s)']:.3e} Pa·s",
            "--------------------------------",
            f"• Diameter D     : {s['Pipe Diameter D (um)']:.2f} µm",
            f"• Radius R       : {s['Pipe Radius R (um)']:.2f} µm",
            f"• Entrance Le    : {s['Entrance Length Le (mm)']:.3f} mm",
            f"• Total Length L : {s['Total Pipe Length L (mm)']:.3f} mm",
            f"• L / Le Ratio   : {s['L / Le Ratio']:.2f}",
            "--------------------------------",
            f"• Max Vel (CFD)  : {s['Outlet Centerline Velocity (m/s)']:.2f} m/s",
            f"• Max Vel (Exact): {s['Theoretical Fully Developed u_max (m/s)']:.2f} m/s",
            f"• Match Accuracy : {s['Centerline Velocity Accuracy (%)']:.2f}%",
            f"• Wall Shear Tw  : {s['Theoretical Wall Shear Stress (kPa)']:.2f} kPa"
        ]
        self.f_summary_txt.insert(tk.END, "\n".join(lines))

        # Render Tabs
        for tab in [self.f_tab1, self.f_tab2, self.f_tab3, self.f_tab4]:
            for child in tab.winfo_children(): child.destroy()

        # Tab 1: 2D Velocity Contour
        fig1, ax1 = plt.subplots(figsize=(8.5, 4.8))
        r_full = np.concatenate([-self.f_sim.r[::-1], self.f_sim.r[1:]]) * 1e6
        u_full = np.concatenate([self.f_sim.u[:, ::-1], self.f_sim.u[:, 1:]], axis=1)
        X_mesh, R_mesh = np.meshgrid(self.f_sim.x * 1e3, r_full)
        levels = np.linspace(0, np.max(self.f_sim.u), 35)
        cf = ax1.contourf(X_mesh, R_mesh, u_full.T, levels=levels, cmap="turbo")
        plt.colorbar(cf, ax=ax1, label="Axial Velocity u(x, r) [m/s]")
        ax1.axvline(x=self.f_sim.Le * 1e3, color="white", linestyle="--", linewidth=1.5, label=f"Entrance Le = {self.f_sim.Le*1e3:.2f} mm")
        ax1.set_title("2D Axial Velocity Field u(x, r) Developing Contour", fontweight="bold")
        ax1.set_xlabel("Axial Distance along Pipe x [mm]")
        ax1.set_ylabel("Radial Coordinate r [µm]")
        ax1.legend(loc="lower right")
        fig1.tight_layout()
        c1 = FigureCanvasTkAgg(fig1, master=self.f_tab1)
        c1.draw(); c1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Tab 2: Profiles
        fig2, ax2 = plt.subplots(figsize=(8.5, 4.8))
        for ratio, col in zip([0.0, 0.05, 0.2, 0.5, 1.0, 1.5], plt.cm.plasma(np.linspace(0.1, 0.9, 6))):
            idx = min(int(round((ratio * self.f_sim.Le / self.f_sim.L) * (self.f_sim.Nx - 1))), self.f_sim.Nx - 1)
            ax2.plot(self.f_sim.u[idx, :], self.f_sim.r / self.f_sim.R, label=f"x/Le = {ratio:.2f}", color=col, linewidth=1.8)
        u_th = self.f_sim.analytical_poiseuille_profile()
        ax2.plot(u_th, self.f_sim.r / self.f_sim.R, "k--", linewidth=2.0, label="Exact Poiseuille")
        ax2.set_title("Radial Velocity Profiles Evolution", fontweight="bold")
        ax2.set_xlabel("Axial Velocity u(r) [m/s]")
        ax2.set_ylabel("Normalized Radius r / R")
        ax2.grid(True, linestyle="--", alpha=0.6)
        ax2.legend()
        fig2.tight_layout()
        c2 = FigureCanvasTkAgg(fig2, master=self.f_tab2)
        c2.draw(); c2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Tab 3: Centerline
        fig3, ax3 = plt.subplots(figsize=(8.5, 4.8))
        ax3.plot(self.f_sim.x / self.f_sim.Le, self.f_sim.u_centerline / self.f_sim.U_in, "b-", linewidth=2.2, label="Numerical uc(x)/Uin")
        ax3.axhline(y=2.0, color="r", linestyle="--", label="Developed Asymptote (2.0)")
        ax3.axvline(x=1.0, color="g", linestyle=":", label="Entrance Threshold (x/Le = 1.0)")
        ax3.set_title("Centerline Velocity Evolution uc(x)/Uin vs x/Le", fontweight="bold")
        ax3.set_xlabel("Normalized Distance x / Le")
        ax3.set_ylabel("uc / Uin")
        ax3.grid(True, linestyle="--", alpha=0.6)
        ax3.legend()
        fig3.tight_layout()
        c3 = FigureCanvasTkAgg(fig3, master=self.f_tab3)
        c3.draw(); c3.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Tab 4: Pressure Drop
        fig4, ax4 = plt.subplots(figsize=(8.5, 4.8))
        ax4.plot(self.f_sim.x * 1e3, (self.f_sim.p[0] - self.f_sim.p)/1e3, "purple", linewidth=2.0, label="Numerical ΔP(x)")
        ax4.plot(self.f_sim.x * 1e3, -self.f_sim.dp_dx_theoretical * self.f_sim.x / 1e3, "k--", label="Poiseuille Linear Slope")
        ax4.axvline(x=self.f_sim.Le * 1e3, color="g", linestyle=":", label="Entrance Le")
        ax4.set_title("Cumulative Pressure Drop ΔP(x) along Pipe", fontweight="bold")
        ax4.set_xlabel("Axial Position x [mm]")
        ax4.set_ylabel("Pressure Drop ΔP [kPa]")
        ax4.grid(True, linestyle="--", alpha=0.6)
        ax4.legend()
        fig4.tight_layout()
        c4 = FigureCanvasTkAgg(fig4, master=self.f_tab4)
        c4.draw(); c4.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def main():
    root = tk.Tk()
    app = UnifiedSuiteApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

