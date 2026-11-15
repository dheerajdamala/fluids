"""
Maze Data Structure and Generation Algorithms.
Defines the grid representation, cell states, neighbor queries,
and generation techniques (Recursive Backtracker, Prim's, Random, Presets).
"""

import random
from collections import deque

# Cell constants
EMPTY = 0
WALL = 1
START = 2
GOAL = 3

class Maze:
    def __init__(self, rows=25, cols=25):
        self.rows = rows
        self.cols = cols
        self.grid = [[EMPTY for _ in range(cols)] for _ in range(rows)]
        self.start = (1, 1)
        self.goal = (rows - 2, cols - 2)
        
        # Ensure default start and goal are empty
        self.grid[self.start[0]][self.start[1]] = START
        self.grid[self.goal[0]][self.goal[1]] = GOAL

    def reset_grid(self):
        """Clears all walls while preserving start and goal positions."""
        self.grid = [[EMPTY for _ in range(self.cols)] for _ in range(self.rows)]
        self.grid[self.start[0]][self.start[1]] = START
        self.grid[self.goal[0]][self.goal[1]] = GOAL

    def is_valid(self, r, c):
        """Check if coordinates lie within grid bounds."""
        return 0 <= r < self.rows and 0 <= c < self.cols

    def is_walkable(self, r, c):
        """Check if cell can be traversed by the robot."""
        return self.is_valid(r, c) and self.grid[r][c] != WALL

    def get_neighbors(self, r, c):
        """
        Returns valid orthogonal neighbors: Up, Right, Down, Left.
        Adheres to 4-connected grid movement constraint.
        """
        neighbors = []
        # Movement directions: Up, Down, Left, Right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if self.is_walkable(nr, nc):
                neighbors.append((nr, nc))
        return neighbors

    def set_wall(self, r, c, is_wall=True):
        """Sets or removes a wall at (r, c), preventing overwrite of start/goal."""
        if not self.is_valid(r, c):
            return False
        if (r, c) == self.start or (r, c) == self.goal:
            return False
        self.grid[r][c] = WALL if is_wall else EMPTY
        return True

    def toggle_wall(self, r, c):
        """Toggles a wall at (r, c)."""
        if not self.is_valid(r, c):
            return
        if (r, c) == self.start or (r, c) == self.goal:
            return
        self.grid[r][c] = EMPTY if self.grid[r][c] == WALL else WALL

    def set_start(self, r, c):
        """Updates the robot's starting position."""
        if not self.is_valid(r, c) or (r, c) == self.goal:
            return False
        old_r, old_c = self.start
        self.grid[old_r][old_c] = EMPTY
        self.start = (r, c)
        self.grid[r][c] = START
        return True

    def set_goal(self, r, c):
        """Updates the target goal position."""
        if not self.is_valid(r, c) or (r, c) == self.start:
            return False
        old_r, old_c = self.goal
        self.grid[old_r][old_c] = EMPTY
        self.goal = (r, c)
        self.grid[r][c] = GOAL
        return True

    # ------------------ Maze Generation Algorithms ------------------

    def generate_random_obstacles(self, density=0.25):
        """Fills the maze with random obstacles according to density probability."""
        self.reset_grid()
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) not in (self.start, self.goal):
                    if random.random() < density:
                        self.grid[r][c] = WALL

    def generate_recursive_backtracker(self):
        """
        Generates a perfect maze using Randomized Depth-First Search
        (Recursive Backtracker). Guaranteed single solution with winding paths.
        Works best when rows and cols are odd.
        """
        # Fill entirely with walls
        self.grid = [[WALL for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Carve starting from (1, 1)
        start_r = 1 if self.rows > 2 else 0
        start_c = 1 if self.cols > 2 else 0
        self.grid[start_r][start_c] = EMPTY
        
        stack = [(start_r, start_c)]
        visited = set([(start_r, start_c)])

        while stack:
            r, c = stack[-1]
            unvisited_neighbors = []
            
            # Check 2 steps away
            for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nr, nc = r + dr, c + dc
                if 0 < nr < self.rows - 1 and 0 < nc < self.cols - 1:
                    if (nr, nc) not in visited:
                        unvisited_neighbors.append((nr, nc, dr, dc))
                        
            if unvisited_neighbors:
                nr, nc, dr, dc = random.choice(unvisited_neighbors)
                # Carve wall between
                self.grid[r + dr // 2][c + dc // 2] = EMPTY
                self.grid[nr][nc] = EMPTY
                visited.add((nr, nc))
                stack.append((nr, nc))
            else:
                stack.pop()

        # Place Start and Goal in open cells
        self.start = (1, 1)
        self.grid[1][1] = START
        
        goal_r = self.rows - 2 if self.rows % 2 == 1 else self.rows - 3
        goal_c = self.cols - 2 if self.cols % 2 == 1 else self.cols - 3
        if goal_r <= 0: goal_r = self.rows - 1
        if goal_c <= 0: goal_c = self.cols - 1
        
        self.goal = (goal_r, goal_c)
        self.grid[goal_r][goal_c] = GOAL

    def generate_prims(self):
        """
        Generates an organic maze with multiple short dead-ends
        using Randomized Prim's Algorithm.
        """
        self.grid = [[WALL for _ in range(self.cols)] for _ in range(self.rows)]
        
        start_r = 1 if self.rows > 2 else 0
        start_c = 1 if self.cols > 2 else 0
        self.grid[start_r][start_c] = EMPTY
        
        walls = []
        for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nr, nc = start_r + dr, start_c + dc
            if 0 < nr < self.rows - 1 and 0 < nc < self.cols - 1:
                walls.append((nr, nc, start_r + dr // 2, start_c + dc // 2))

        while walls:
            idx = random.randrange(len(walls))
            nr, nc, mr, mc = walls.pop(idx)
            
            if self.grid[nr][nc] == WALL:
                self.grid[mr][mc] = EMPTY
                self.grid[nr][nc] = EMPTY
                
                for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                    nnr, nnc = nr + dr, nc + dc
                    if 0 < nnr < self.rows - 1 and 0 < nnc < self.cols - 1:
                        if self.grid[nnr][nnc] == WALL:
                            walls.append((nnr, nnc, nr + dr // 2, nc + dc // 2))

        self.start = (1, 1)
        self.grid[1][1] = START
        goal_r = self.rows - 2
        goal_c = self.cols - 2
        self.grid[goal_r][goal_c] = GOAL
        self.goal = (goal_r, goal_c)

    def generate_preset(self, preset_name):
        """Loads structured scenarios designed to test search behavior."""
        self.reset_grid()
        r_mid = self.rows // 2
        c_mid = self.cols // 2

        if preset_name == "Bottleneck":
            # Wall dividing the room with a single narrow gap
            for r in range(self.rows):
                if r != r_mid:
                    self.grid[r][c_mid] = WALL
            self.start = (r_mid, 2)
            self.goal = (r_mid, self.cols - 3)
            self.grid[self.start[0]][self.start[1]] = START
            self.grid[self.goal[0]][self.goal[1]] = GOAL

        elif preset_name == "Spiral":
            # Coiling wall forces algorithms to travel in an inward spiral
            top, bottom, left, right = 0, self.rows - 1, 0, self.cols - 1
            step = 2
            while top + step < bottom and left + step < right:
                for c in range(left + step, right - step + 1):
                    self.grid[top + step][c] = WALL
                for r in range(top + step, bottom - step + 1):
                    self.grid[r][right - step] = WALL
                for c in range(right - step, left + step, -1):
                    self.grid[bottom - step][c] = WALL
                for r in range(bottom - step, top + step + 2, -1):
                    self.grid[r][left + step] = WALL
                top += step + 1
                bottom -= step + 1
                left += step + 1
                right -= step + 1

            self.start = (1, 1)
            self.goal = (r_mid, c_mid)
            self.grid[self.start[0]][self.start[1]] = START
            self.grid[self.goal[0]][self.goal[1]] = GOAL

        elif preset_name == "Multi-Room":
            # Divide grid into 4 chambers with doorways
            for r in range(self.rows):
                if r not in (self.rows // 4, 3 * self.rows // 4):
                    self.grid[r][c_mid] = WALL
            for c in range(self.cols):
                if c not in (self.cols // 4, 3 * self.cols // 4):
                    self.grid[r_mid][c] = WALL
            self.start = (2, 2)
            self.goal = (self.rows - 3, self.cols - 3)
            self.grid[self.start[0]][self.start[1]] = START
            self.grid[self.goal[0]][self.goal[1]] = GOAL

        elif preset_name == "Trap / Local Minima":
            # Horseshoe trap opening away from goal to trap greedy searches
            box_r, box_c = r_mid, c_mid
            for r in range(box_r - 4, box_r + 5):
                self.grid[r][box_c + 3] = WALL
            for c in range(box_c - 4, box_c + 4):
                self.grid[box_r - 4][c] = WALL
                self.grid[box_r + 4][c] = WALL
            self.start = (box_r, box_c)
            self.goal = (box_r, box_c + 6)
            self.grid[self.start[0]][self.start[1]] = START
            self.grid[self.goal[0]][self.goal[1]] = GOAL

