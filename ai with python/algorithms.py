"""
Artificial Intelligence Search Algorithms for 2D Maze Solving Robot.
Implements:
1. Breadth-First Search (BFS) - Uninformed, Guarantees shortest path
2. Depth-First Search (DFS) - Uninformed, Deep exploration, not optimal
3. Uniform Cost Search (UCS / Dijkstra) - Uninformed, Optimal cost-based
4. A* Search (Manhattan Heuristic) - Informed, Optimal & Admissible
5. A* Search (Euclidean Heuristic) - Informed, Optimal & Admissible
6. Greedy Best-First Search - Informed, Goal-directed heuristic search
"""

import time
import math
import heapq
from collections import deque

class SearchResult:
    """Encapsulates the outcome and performance metrics of a search run."""
    def __init__(self, name, success, path, explored_order, max_frontier, exec_time_ms):
        self.name = name
        self.success = success
        self.path = path or []
        self.path_length = max(0, len(self.path) - 1)
        self.explored_order = explored_order or []
        self.nodes_explored = len(self.explored_order)
        self.max_frontier = max_frontier
        self.execution_time_ms = exec_time_ms

    def summary(self):
        return (
            f"[{self.name}]\n"
            f"  Success: {'YES' if self.success else 'NO'}\n"
            f"  Path Length: {self.path_length} steps\n"
            f"  Nodes Explored: {self.nodes_explored}\n"
            f"  Peak Frontier: {self.max_frontier}\n"
            f"  Execution Time: {self.execution_time_ms:.3f} ms"
        )


# ------------------ Heuristic Functions ------------------

def manhattan_distance(p1, p2):
    """
    Manhattan distance: |r1 - r2| + |c1 - c2|
    Admissible and consistent for 4-directional grid movement.
    """
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def euclidean_distance(p1, p2):
    """
    Euclidean straight-line distance: sqrt((r1-r2)^2 + (c1-c2)^2)
    Admissible lower bound for grid traversal.
    """
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def reconstruct_path(parent_map, start, goal):
    """Traces parent pointers from goal to start to produce solution path."""
    curr = goal
    path = []
    while curr is not None:
        path.append(curr)
        curr = parent_map.get(curr)
    path.reverse()
    return path if path and path[0] == start else []


# ------------------ Algorithm Implementations ------------------

def bfs(maze):
    """
    Breadth-First Search (BFS):
    Explores shallowest unvisited nodes first using a FIFO Queue.
    Guarantees the shortest path on an unweighted grid.
    Time Complexity: O(V + E)
    Space Complexity: O(V)
    """
    start_time = time.perf_counter()
    start, goal = maze.start, maze.goal
    
    if start == goal:
        return SearchResult("BFS", True, [start], [start], 1, 0.0)

    queue = deque([start])
    visited = {start}
    parent = {start: None}
    explored_order = []
    max_frontier = 1

    while queue:
        max_frontier = max(max_frontier, len(queue))
        curr = queue.popleft()
        explored_order.append(curr)

        if curr == goal:
            exec_time = (time.perf_counter() - start_time) * 1000.0
            path = reconstruct_path(parent, start, goal)
            return SearchResult("BFS", True, path, explored_order, max_frontier, exec_time)

        for neighbor in maze.get_neighbors(curr[0], curr[1]):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = curr
                queue.append(neighbor)

    exec_time = (time.perf_counter() - start_time) * 1000.0
    return SearchResult("BFS", False, [], explored_order, max_frontier, exec_time)


def dfs(maze):
    """
    Depth-First Search (DFS):
    Explores along each branch as deeply as possible using a LIFO Stack.
    Does NOT guarantee the shortest path; may wander into dead ends.
    Time Complexity: O(V + E)
    Space Complexity: O(V)
    """
    start_time = time.perf_counter()
    start, goal = maze.start, maze.goal
    
    if start == goal:
        return SearchResult("DFS", True, [start], [start], 1, 0.0)

    stack = [start]
    visited = {start}
    parent = {start: None}
    explored_order = []
    max_frontier = 1

    while stack:
        max_frontier = max(max_frontier, len(stack))
        curr = stack.pop()
        explored_order.append(curr)

        if curr == goal:
            exec_time = (time.perf_counter() - start_time) * 1000.0
            path = reconstruct_path(parent, start, goal)
            return SearchResult("DFS", True, path, explored_order, max_frontier, exec_time)

        # Explore neighbors
        for neighbor in maze.get_neighbors(curr[0], curr[1]):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = curr
                stack.append(neighbor)

    exec_time = (time.perf_counter() - start_time) * 1000.0
    return SearchResult("DFS", False, [], explored_order, max_frontier, exec_time)


def uniform_cost_search(maze):
    """
    Uniform Cost Search (UCS / Dijkstra):
    Expands the node with lowest path cost g(n) using a Priority Queue.
    Equivalent to Dijkstra's algorithm. Optimal for arbitrary non-negative costs.
    Time Complexity: O((V + E) log V)
    Space Complexity: O(V)
    """
    start_time = time.perf_counter()
    start, goal = maze.start, maze.goal
    
    if start == goal:
        return SearchResult("Uniform Cost Search", True, [start], [start], 1, 0.0)

    # Priority queue holds (g_cost, tiebreaker, node)
    counter = 0
    pq = [(0, counter, start)]
    g_costs = {start: 0}
    parent = {start: None}
    visited = set()
    explored_order = []
    max_frontier = 1

    while pq:
        max_frontier = max(max_frontier, len(pq))
        curr_g, _, curr = heapq.heappop(pq)

        if curr in visited:
            continue
        visited.add(curr)
        explored_order.append(curr)

        if curr == goal:
            exec_time = (time.perf_counter() - start_time) * 1000.0
            path = reconstruct_path(parent, start, goal)
            return SearchResult("Uniform Cost Search", True, path, explored_order, max_frontier, exec_time)

        for neighbor in maze.get_neighbors(curr[0], curr[1]):
            cost = curr_g + 1  # Unit step cost
            if neighbor not in g_costs or cost < g_costs[neighbor]:
                g_costs[neighbor] = cost
                parent[neighbor] = curr
                counter += 1
                heapq.heappush(pq, (cost, counter, neighbor))

    exec_time = (time.perf_counter() - start_time) * 1000.0
    return SearchResult("Uniform Cost Search", False, [], explored_order, max_frontier, exec_time)


def a_star(maze, heuristic_func=manhattan_distance, heuristic_name="Manhattan"):
    """
    A* Search Algorithm:
    Evaluates nodes by f(n) = g(n) + h(n), balancing path cost g(n)
    and heuristic estimate h(n) using a Priority Queue.
    Guarantees optimal solution with admissible and consistent heuristics.
    Time Complexity: O(E) in best case, O(b^d) in worst case
    Space Complexity: O(V)
    """
    start_time = time.perf_counter()
    start, goal = maze.start, maze.goal
    algo_name = f"A* Search ({heuristic_name})"
    
    if start == goal:
        return SearchResult(algo_name, True, [start], [start], 1, 0.0)

    counter = 0
    h_start = heuristic_func(start, goal)
    # PQ entries: (f_score, h_score, counter, node)
    pq = [(h_start, h_start, counter, start)]
    g_costs = {start: 0}
    parent = {start: None}
    visited = set()
    explored_order = []
    max_frontier = 1

    while pq:
        max_frontier = max(max_frontier, len(pq))
        curr_f, curr_h, _, curr = heapq.heappop(pq)

        if curr in visited:
            continue
        visited.add(curr)
        explored_order.append(curr)

        if curr == goal:
            exec_time = (time.perf_counter() - start_time) * 1000.0
            path = reconstruct_path(parent, start, goal)
            return SearchResult(algo_name, True, path, explored_order, max_frontier, exec_time)

        for neighbor in maze.get_neighbors(curr[0], curr[1]):
            tentative_g = g_costs[curr] + 1
            if neighbor not in g_costs or tentative_g < g_costs[neighbor]:
                g_costs[neighbor] = tentative_g
                h = heuristic_func(neighbor, goal)
                f = tentative_g + h
                parent[neighbor] = curr
                counter += 1
                heapq.heappush(pq, (f, h, counter, neighbor))

    exec_time = (time.perf_counter() - start_time) * 1000.0
    return SearchResult(algo_name, False, [], explored_order, max_frontier, exec_time)


def greedy_best_first_search(maze, heuristic_func=manhattan_distance, heuristic_name="Manhattan"):
    """
    Greedy Best-First Search:
    Expands nodes based purely on heuristic distance to goal: f(n) = h(n).
    Can be significantly faster in open areas, but is NOT optimal and
    can be led astray by obstacle traps and local minima.
    Time Complexity: O(b^m) worst case
    Space Complexity: O(b^m)
    """
    start_time = time.perf_counter()
    start, goal = maze.start, maze.goal
    algo_name = f"Greedy Best-First ({heuristic_name})"
    
    if start == goal:
        return SearchResult(algo_name, True, [start], [start], 1, 0.0)

    counter = 0
    h_start = heuristic_func(start, goal)
    pq = [(h_start, counter, start)]
    visited = {start}
    parent = {start: None}
    explored_order = []
    max_frontier = 1

    while pq:
        max_frontier = max(max_frontier, len(pq))
        _, _, curr = heapq.heappop(pq)
        explored_order.append(curr)

        if curr == goal:
            exec_time = (time.perf_counter() - start_time) * 1000.0
            path = reconstruct_path(parent, start, goal)
            return SearchResult(algo_name, True, path, explored_order, max_frontier, exec_time)

        for neighbor in maze.get_neighbors(curr[0], curr[1]):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = curr
                counter += 1
                h = heuristic_func(neighbor, goal)
                heapq.heappush(pq, (h, counter, neighbor))

    exec_time = (time.perf_counter() - start_time) * 1000.0
    return SearchResult(algo_name, False, [], explored_order, max_frontier, exec_time)


# Dictionary mapping friendly keys to runner functions
ALGORITHMS = {
    "A* Search (Manhattan)": lambda m: a_star(m, manhattan_distance, "Manhattan"),
    "A* Search (Euclidean)": lambda m: a_star(m, euclidean_distance, "Euclidean"),
    "Breadth-First Search (BFS)": bfs,
    "Depth-First Search (DFS)": dfs,
    "Greedy Best-First (Manhattan)": lambda m: greedy_best_first_search(m, manhattan_distance, "Manhattan"),
    "Uniform Cost Search (UCS)": uniform_cost_search,
}

