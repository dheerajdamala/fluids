"""
2D Robot Entity for Maze Navigation and Visualization.
Features directional orientation, headlamps beam, sensor eyes,
tread animation, and smooth path traversal.
"""

import math

class Robot:
    def __init__(self, start_pos=(1, 1)):
        self.r = start_pos[0]
        self.c = start_pos[1]
        self.target_r = self.r
        self.target_c = self.c
        self.angle = 0.0  # In degrees: 0 = East, 90 = South, 180 = West, 270 = North
        self.target_angle = 0.0
        self.steps_taken = 0
        self.path = []
        self.path_index = 0
        self.is_navigating = False
        self.is_finished = False
        self.trail = []

    def reset(self, start_pos=(1, 1)):
        """Resets the robot to initial state and position."""
        self.r = start_pos[0]
        self.c = start_pos[1]
        self.target_r = self.r
        self.target_c = self.c
        self.angle = 0.0
        self.target_angle = 0.0
        self.steps_taken = 0
        self.path = []
        self.path_index = 0
        self.is_navigating = False
        self.is_finished = False
        self.trail = [(self.r, self.c)]

    def set_path(self, path):
        """Assigns the computed solution path to the robot."""
        self.path = path
        self.path_index = 0
        self.steps_taken = 0
        self.is_finished = False
        self.trail = []
        if path:
            self.r, self.c = path[0]
            self.target_r, self.target_c = path[0]
            self.trail = [path[0]]
            self.is_navigating = True

    def step(self):
        """Advances the robot by one cell along the path."""
        if not self.is_navigating or self.path_index >= len(self.path) - 1:
            self.is_navigating = False
            self.is_finished = True
            return False

        self.path_index += 1
        next_r, next_c = self.path[self.path_index]
        
        # Calculate orientation angle
        dr = next_r - self.r
        dc = next_c - self.c
        if dc > 0:
            self.angle = 0.0    # Right / East
        elif dr > 0:
            self.angle = 90.0   # Down / South
        elif dc < 0:
            self.angle = 180.0  # Left / West
        elif dr < 0:
            self.angle = 270.0  # Up / North

        self.r = next_r
        self.c = next_c
        self.trail.append((next_r, next_c))
        self.steps_taken += 1

        if self.path_index == len(self.path) - 1:
            self.is_navigating = False
            self.is_finished = True

        return True

    def draw(self, canvas, cell_size, offset_x=0, offset_y=0, pulse_frame=0):
        """
        Renders the 2D robot onto the Tkinter canvas with chassis,
        directional headlight beam, sensor eyes, and treads.
        """
        cx = offset_x + (self.c + 0.5) * cell_size
        cy = offset_y + (self.r + 0.5) * cell_size
        radius = cell_size * 0.40

        # Draw headlight beam cone in front of robot
        rad = math.radians(self.angle)
        beam_dist = cell_size * 1.2
        spread = math.radians(28)
        p1 = (cx, cy)
        p2 = (cx + beam_dist * math.cos(rad - spread), cy + beam_dist * math.sin(rad - spread))
        p3 = (cx + beam_dist * math.cos(rad + spread), cy + beam_dist * math.sin(rad + spread))
        
        canvas.create_polygon(
            p1[0], p1[1], p2[0], p2[1], p3[0], p3[1],
            fill="#FFF59D", outline="", stipple="gray25", tags="robot"
        )

        # Wheels / Treads (rectangles rotated perpendicular to direction)
        tread_w = radius * 1.8
        tread_h = radius * 0.35
        # Perpendicular angle
        perp_rad = rad + math.pi / 2
        offset_dist = radius * 0.85
        for sign in [-1, 1]:
            tx = cx + sign * offset_dist * math.cos(perp_rad)
            ty = cy + sign * offset_dist * math.sin(perp_rad)
            canvas.create_oval(
                tx - radius * 0.3, ty - radius * 0.3,
                tx + radius * 0.3, ty + radius * 0.3,
                fill="#263238", outline="#37474F", width=2, tags="robot"
            )

        # Main Chassis (Cyan / Teal metallic body)
        canvas.create_oval(
            cx - radius, cy - radius,
            cx + radius, cy + radius,
            fill="#00E5FF", outline="#00838F", width=2, tags="robot"
        )

        # Inner Circuit Core
        inner_r = radius * 0.65
        canvas.create_oval(
            cx - inner_r, cy - inner_r,
            cx + inner_r, cy + inner_r,
            fill="#0097A7", outline="#006064", width=1, tags="robot"
        )

        # Directional Sensor Eyes / Camera
        eye_offset = radius * 0.45
        eye_rad = rad
        eye_cx = cx + eye_offset * math.cos(eye_rad)
        eye_cy = cy + eye_offset * math.sin(eye_rad)
        eye_size = radius * 0.28
        
        # Dual binocular lenses
        for side in [-1, 1]:
            lx = eye_cx + side * (radius * 0.25) * math.cos(perp_rad)
            ly = eye_cy + side * (radius * 0.25) * math.sin(perp_rad)
            canvas.create_oval(
                lx - eye_size, ly - eye_size,
                lx + eye_size, ly + eye_size,
                fill="#FFFFFF", outline="#004D40", width=1, tags="robot"
            )
            # Glowing pupil
            pupil_size = eye_size * 0.5
            canvas.create_oval(
                lx - pupil_size, ly - pupil_size,
                lx + pupil_size, ly + pupil_size,
                fill="#FF1744", outline="", tags="robot"
            )

        # Central Antenna / Beacon LED
        antenna_r = radius * 0.18
        beacon_color = "#FF5252" if (pulse_frame // 4) % 2 == 0 else "#FFD700"
        canvas.create_oval(
            cx - antenna_r, cy - antenna_r,
            cx + antenna_r, cy + antenna_r,
            fill=beacon_color, outline="#B71C1C", width=1, tags="robot"
        )

        # If goal reached, draw celebratory victory pulse
        if self.is_finished:
            pulse_r = radius * 1.5 + (pulse_frame % 8) * 3
            canvas.create_oval(
                cx - pulse_r, cy - pulse_r,
                cx + pulse_r, cy + pulse_r,
                outline="#00E676", width=2, tags="robot"
            )

