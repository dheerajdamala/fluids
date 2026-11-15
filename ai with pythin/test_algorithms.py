"""
Automated Unit and Integration Tests for AI Maze Solving Robot.
Verifies algorithm correctness, path optimality, admissibility,
unsolvable state handling, and robot state progression.
"""

import unittest
from maze import Maze, WALL, EMPTY
from algorithms import (
    bfs,
    dfs,
    uniform_cost_search,
    a_star,
    greedy_best_first_search,
    manhattan_distance,
    euclidean_distance
)
from robot import Robot

class TestMazeAndAlgorithms(unittest.TestCase):
    def setUp(self):
        self.maze = Maze(15, 15)

    def test_open_grid_optimality(self):
        """On an open grid with no obstacles, BFS, UCS, and A* must achieve Manhattan distance."""
        self.maze.reset_grid()
        self.maze.set_start(1, 1)
        self.maze.set_goal(10, 10)
        expected_optimal_len = manhattan_distance((1, 1), (10, 10))

        res_bfs = bfs(self.maze)
        res_ucs = uniform_cost_search(self.maze)
        res_astar_man = a_star(self.maze, manhattan_distance, "Manhattan")
        res_astar_euc = a_star(self.maze, euclidean_distance, "Euclidean")

        self.assertTrue(res_bfs.success)
        self.assertTrue(res_ucs.success)
        self.assertTrue(res_astar_man.success)
        self.assertTrue(res_astar_euc.success)

        self.assertEqual(res_bfs.path_length, expected_optimal_len)
        self.assertEqual(res_ucs.path_length, expected_optimal_len)
        self.assertEqual(res_astar_man.path_length, expected_optimal_len)
        self.assertEqual(res_astar_euc.path_length, expected_optimal_len)

    def test_astar_efficiency_vs_bfs(self):
        """A* with Manhattan heuristic must explore fewer or equal states than uninformed BFS on open grid."""
        self.maze.reset_grid()
        self.maze.set_start(1, 1)
        self.maze.set_goal(13, 13)

        res_bfs = bfs(self.maze)
        res_astar = a_star(self.maze, manhattan_distance, "Manhattan")

        self.assertTrue(res_astar.nodes_explored <= res_bfs.nodes_explored)
        self.assertEqual(res_astar.path_length, res_bfs.path_length)

    def test_blocked_goal_detection(self):
        """When goal is walled in, all algorithms must gracefully return success=False."""
        self.maze.reset_grid()
        gr, gc = self.maze.goal
        # Enclose goal with walls
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = gr + dr, gc + dc
            if self.maze.is_valid(nr, nc):
                self.maze.set_wall(nr, nc, True)

        for algo in [bfs, dfs, uniform_cost_search,
                     lambda m: a_star(m, manhattan_distance, "Manhattan"),
                     lambda m: greedy_best_first_search(m, manhattan_distance, "Manhattan")]:
            res = algo(self.maze)
            self.assertFalse(res.success, f"{res.name} should fail when goal is unreachable")
            self.assertEqual(res.path_length, 0)
            self.assertEqual(len(res.path), 0)

    def test_recursive_maze_solvability(self):
        """A recursive backtracker maze must have a valid path between start and goal."""
        self.maze.generate_recursive_backtracker()
        res_bfs = bfs(self.maze)
        self.assertTrue(res_bfs.success, "Recursive backtracker maze should always be solvable")
        self.assertGreater(res_bfs.path_length, 0)

    def test_robot_traversal(self):
        """Robot must initialize at start, step through path, and finish at goal."""
        self.maze.generate_recursive_backtracker()
        res = a_star(self.maze, manhattan_distance, "Manhattan")
        self.assertTrue(res.success)

        robot = Robot(self.maze.start)
        robot.set_path(res.path)
        self.assertTrue(robot.is_navigating)
        self.assertFalse(robot.is_finished)

        # Step through path
        step_count = 0
        while robot.step():
            step_count += 1

        self.assertFalse(robot.is_navigating)
        self.assertTrue(robot.is_finished)
        self.assertEqual(robot.steps_taken, res.path_length)
        self.assertEqual((robot.r, robot.c), self.maze.goal)

if __name__ == "__main__":
    unittest.main()

