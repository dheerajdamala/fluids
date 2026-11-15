"""
Comparative Performance Analysis Module.
Runs all implemented search algorithms on the same maze configuration,
calculates efficiency and optimality metrics, logs tabular outputs,
and generates graphical comparison charts using Matplotlib.
"""

import os
import csv
import matplotlib.pyplot as plt
from algorithms import (
    bfs,
    dfs,
    uniform_cost_search,
    a_star,
    greedy_best_first_search,
    manhattan_distance,
    euclidean_distance
)

def run_all_comparisons(maze):
    """
    Executes all search algorithms on the provided maze instance.
    Returns a dictionary of SearchResult objects.
    """
    results = []

    # Run BFS
    results.append(bfs(maze))

    # Run DFS
    results.append(dfs(maze))

    # Run UCS
    results.append(uniform_cost_search(maze))

    # Run A* Manhattan
    results.append(a_star(maze, manhattan_distance, "Manhattan"))

    # Run A* Euclidean
    results.append(a_star(maze, euclidean_distance, "Euclidean"))

    # Run Greedy Best-First
    results.append(greedy_best_first_search(maze, manhattan_distance, "Manhattan"))

    return results


def print_comparison_table(results):
    """Prints a formatted ASCII comparison table to stdout."""
    header = f"{'Algorithm':<32} | {'Success':<8} | {'Path (Steps)':<13} | {'Explored':<10} | {'Frontier':<10} | {'Time (ms)':<10}"
    sep = "-" * len(header)
    print("\n" + "=" * len(header))
    print("           AI MAZE SOLVING ROBOT - ALGORITHM PERFORMANCE BENCHMARK")
    print("=" * len(header))
    print(header)
    print(sep)
    for r in results:
        succ_str = "YES" if r.success else "NO"
        print(f"{r.name:<32} | {succ_str:<8} | {r.path_length:<13} | {r.nodes_explored:<10} | {r.max_frontier:<10} | {r.execution_time_ms:<10.3f}")
    print(sep + "\n")


def export_results_csv(results, filepath="comparison_results.csv"):
    """Saves benchmark results to a CSV file."""
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Algorithm", "Success", "Path_Length_Steps", "Nodes_Explored", "Max_Frontier_Size", "Execution_Time_ms"])
        for r in results:
            writer.writerow([r.name, r.success, r.path_length, r.nodes_explored, r.max_frontier, round(r.execution_time_ms, 3)])
    print(f"Benchmark results exported to {filepath}")


def generate_comparison_plots(results, save_path="comparison_chart.png", show_window=False):
    """
    Generates high-resolution comparative bar charts comparing:
    1. Nodes Explored (Search Efficiency)
    2. Path Length (Solution Optimality)
    3. Execution Time (ms)
    """
    names = [r.name for r in results]
    explored = [r.nodes_explored for r in results]
    path_lens = [r.path_length for r in results]
    exec_times = [r.execution_time_ms for r in results]

    colors = ['#1E88E5', '#D81B60', '#8E24AA', '#00897B', '#43A047', '#FB8C00']

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Comparative Evaluation of AI Search Algorithms for Maze-Solving Robot", fontsize=14, fontweight='bold')

    # 1. Nodes Explored
    bars1 = axes[0].barh(names, explored, color=colors)
    axes[0].set_title("Explored Nodes (Lower = More Efficient)")
    axes[0].set_xlabel("Number of States Expanded")
    axes[0].grid(axis='x', linestyle='--', alpha=0.6)
    for bar in bars1:
        w = bar.get_width()
        axes[0].annotate(f'{int(w)}', (w, bar.get_y() + bar.get_height() / 2),
                         xytext=(3, 0), textcoords="offset points", va='center', fontsize=9)

    # 2. Path Length
    bars2 = axes[1].barh(names, path_lens, color=colors)
    axes[1].set_title("Path Length / Solution Cost (Steps)")
    axes[1].set_xlabel("Path Steps from Start to Goal")
    axes[1].grid(axis='x', linestyle='--', alpha=0.6)
    for bar in bars2:
        w = bar.get_width()
        axes[1].annotate(f'{int(w)}', (w, bar.get_y() + bar.get_height() / 2),
                         xytext=(3, 0), textcoords="offset points", va='center', fontsize=9)

    # 3. Execution Time
    bars3 = axes[2].barh(names, exec_times, color=colors)
    axes[2].set_title("Execution Time (Milliseconds)")
    axes[2].set_xlabel("CPU Time (ms)")
    axes[2].grid(axis='x', linestyle='--', alpha=0.6)
    for bar in bars3:
        w = bar.get_width()
        axes[2].annotate(f'{w:.2f}', (w, bar.get_y() + bar.get_height() / 2),
                         xytext=(3, 0), textcoords="offset points", va='center', fontsize=9)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    print(f"Comparison chart saved to {save_path}")

    if show_window:
        plt.show()
    else:
        plt.close(fig)

