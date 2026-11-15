"""
Main Entry Point for AI Maze Solving Robot Application.
Supports:
1. Interactive 2D Visualizer GUI (Default)
2. Headless CLI Benchmarking & Evaluation Mode (--benchmark)
"""

import sys
import argparse
from maze import Maze
from comparison import run_all_comparisons, print_comparison_table, export_results_csv, generate_comparison_plots

def run_benchmark_mode(args):
    print("=" * 70)
    print("      AI MAZE SOLVING ROBOT - HEADLESS BENCHMARK SUITE")
    print("=" * 70)
    print(f"Grid Dimensions: {args.rows}x{args.cols}")
    print(f"Preset / Maze Type: {args.maze_type}")

    maze = Maze(args.rows, args.cols)
    if args.maze_type == "recursive":
        maze.generate_recursive_backtracker()
    elif args.maze_type == "prims":
        maze.generate_prims()
    elif args.maze_type == "random":
        maze.generate_random_obstacles(0.25)
    elif args.maze_type == "bottleneck":
        maze.generate_preset("Bottleneck")
    elif args.maze_type == "spiral":
        maze.generate_preset("Spiral")
    elif args.maze_type == "multi-room":
        maze.generate_preset("Multi-Room")
    elif args.maze_type == "trap":
        maze.generate_preset("Trap / Local Minima")

    results = run_all_comparisons(maze)
    print_comparison_table(results)

    chart_file = "benchmark_comparison.png"
    csv_file = "benchmark_results.csv"
    export_results_csv(results, csv_file)
    generate_comparison_plots(results, save_path=chart_file, show_window=False)

    print(f"Benchmark finished successfully. Artifacts created:")
    print(f"  - Chart: {chart_file}")
    print(f"  - Data:  {csv_file}")


def main():
    parser = argparse.ArgumentParser(description="Smart AI Maze-Solving Robot Visualizer & Benchmarker")
    parser.add_argument("--benchmark", action="store_true", help="Run in headless benchmark mode without launching GUI")
    parser.add_argument("--rows", type=int, default=25, help="Number of grid rows (default: 25)")
    parser.add_argument("--cols", type=int, default=25, help="Number of grid columns (default: 25)")
    parser.add_argument("--maze-type", type=str, default="recursive",
                        choices=["recursive", "prims", "random", "bottleneck", "spiral", "multi-room", "trap"],
                        help="Maze type for benchmark mode")

    args = parser.parse_args()

    if args.benchmark:
        run_benchmark_mode(args)
    else:
        # Launch Interactive GUI
        from gui import launch_gui
        print("Launching AI Maze-Solving Robot Visualizer GUI...")
        launch_gui(args.rows, args.cols)

if __name__ == "__main__":
    main()

