"""
Robot physics model for circular omniwheel robot.

Physical Configuration:
           N (wheel)
            ═══
             │
    W ║──────●──────║ E
      ║      │      ║
            ═══
           S (wheel)

- Circular body with 4 omniwheels at N/S/E/W poles
- North/South wheels: horizontal, control left/right (strafe)
- East/West wheels: vertical, control forward/back
- All wheels same direction = rotation
"""

import math
import random


class Robot:
    """
    Simulates physics for a circular omniwheel robot.
    """

    def __init__(self, x=0.0, y=0.0, theta=0, motor_noise=False):
        """
        Initialize robot at given position and orientation.

        Args:
            x: Initial x position (meters)
            y: Initial y position (meters)
            theta: Initial orientation (radians, 0=facing +X, pi/2=facing +Y)
            motor_noise: If True, add small random fluctuations to motor speeds
        """
        # Position and orientation
        self.x = x
        self.y = y
        self.theta = theta  # radians, 0 = facing right (+X), pi/2 = facing up (+Y)

        # Velocities (in world frame)
        self.vx = 0.0  # m/s
        self.vy = 0.0  # m/s
        self.omega = 0.0  # rad/s

        # Physical parameters
        self.radius = 0.075  # Robot radius: 7.5cm (15cm diameter)
        self.mass = 1.5  # kg
        self.wheel_radius = 0.025  # Wheel radius: 2.5cm

        # Motor parameters
        self.max_wheel_speed = 1.0  # Normalized max speed input
        self.max_linear_speed = 0.5  # m/s at full throttle
        self.max_angular_speed = 4.0  # rad/s at full throttle

        # Target motor speeds (what the controller commands)
        self.target_speeds = {
            "north": 0.0,
            "south": 0.0,
            "east": 0.0,
            "west": 0.0,
        }

        # Actual motor speeds (with lag applied)
        self.actual_speeds = {
            "north": 0.0,
            "south": 0.0,
            "east": 0.0,
            "west": 0.0,
        }

        # Motor noise
        self.motor_noise = motor_noise
        self.motor_noise_amount = 0.03  # ±3% of target speed

        # Physics parameters
        self.motor_tau = 0.05  # Motor response time constant (50ms)

    def set_motor_speed(self, wheel, speed):
        """
        Set target speed for a specific wheel motor.

        Args:
            wheel: "north", "south", "east", or "west"
            speed: Target speed (-1.0 to 1.0, positive = forward)
        """
        if wheel in self.target_speeds:
            # Clamp speed to valid range
            self.target_speeds[wheel] = max(-1.0, min(1.0, float(speed)))

    def get_motor_speed(self, wheel):
        """Get current actual speed of a wheel motor."""
        return self.actual_speeds.get(wheel, 0.0)

    def _update_motor_speeds(self, dt):
        """
        Apply first-order lag to motor speeds (simulates motor response time).
        Optionally adds small random fluctuations to simulate real motor imprecision.
        """
        alpha = dt / (self.motor_tau + dt)  # Smoothing factor

        for wheel in self.actual_speeds:
            target = self.target_speeds[wheel]
            actual = self.actual_speeds[wheel]
            # First-order lag filter
            self.actual_speeds[wheel] = actual + alpha * (target - actual)

            # Add motor noise: small random fluctuation when motor is running
            if self.motor_noise and abs(self.actual_speeds[wheel]) > 0.01:
                noise = random.gauss(0, self.motor_noise_amount)
                self.actual_speeds[wheel] += noise
                self.actual_speeds[wheel] = max(-1.0, min(1.0, self.actual_speeds[wheel]))

    def _calculate_body_velocities(self):
        """
        Calculate robot velocity in body frame from wheel speeds.

        Returns:
            (vx_body, vy_body, omega): Velocities in robot's local frame
        """
        n = self.actual_speeds["north"]
        s = self.actual_speeds["south"]
        e = self.actual_speeds["east"]
        w = self.actual_speeds["west"]

        # Forward kinematics for N/S/E/W omniwheel configuration:
        #
        # Each wheel is tangent to the circle at its position.
        # Positive wheel speed = wheel rotates to push in tangent direction.
        #
        # Wheel positions and tangent directions:
        # - East wheel at (+R, 0): tangent points -Y (positive spin → -Y force)
        # - West wheel at (-R, 0): tangent points +Y (positive spin → +Y force)
        # - North wheel at (0, +R): tangent points +X (positive spin → +X force)
        # - South wheel at (0, -R): tangent points -X (positive spin → -X force)
        #
        # Robot body frame: +X = right, +Y = forward

        # Forward/backward (Y axis): W pushes +Y, E pushes -Y
        # For forward motion: W forward (positive), E backward (negative)
        # Net Y = (W - E) contribution
        vy_body = (w - e) / 2.0 * self.max_linear_speed

        # Strafe left/right (X axis): N pushes +X, S pushes -X
        # For rightward motion: N forward (positive), S backward (negative)
        # Net X = (N - S) contribution... but wait, S pushes -X, so S forward = -X
        # Actually: N forward → +X, S forward → -X
        # For pure +X strafe: N forward, S backward → (N - (-S)) = N + S? No...
        # Let's think again: S at (0,-R) with tangent pointing -X means S forward → force in -X
        # So for +X motion: N forward (+X) and S backward (not -X, but reduced -X)
        # vx = (N contribution) + (S contribution) = N * (+1) + S * (-1) = N - S...
        # Hmm, but the notes say (s - n). Let me reconsider.
        #
        # If S positive → force in -X direction, then S contributes -S to vx
        # If N positive → force in +X direction, then N contributes +N to vx
        # vx = N - S seems right for: N=1, S=0 → vx=1 (rightward) ✓
        # But for pure rotation (all=1): vx = 1 - 1 = 0 ✓
        #
        # The issue noted was about E/W, not N/S. Let me focus on that.
        # With corrected vy = (w - e): all=1 → vy = 1-1 = 0 ✓
        vx_body = (n - s) / 2.0 * self.max_linear_speed

        # Angular velocity: all wheels tangent to circle, all contribute to rotation
        # All wheels forward = all push tangentially = rotation
        # Sign: if +omega = CCW, need to verify which way wheels push
        # All positive wheel speeds create CW rotation (looking down at robot)
        # CW = negative omega in standard math convention
        omega = -(n + s + e + w) / 4.0 * self.max_angular_speed

        return vx_body, vy_body, omega

    def update(self, dt):
        """
        Update robot physics for one timestep.

        Args:
            dt: Time step in seconds
        """
        # Update motor speeds with lag (simulates motor response time)
        self._update_motor_speeds(dt)

        # Calculate velocities in body frame from wheel speeds
        vx_body, vy_body, omega_body = self._calculate_body_velocities()

        # Transform body velocities to world frame
        cos_theta = math.cos(self.theta)
        sin_theta = math.sin(self.theta)

        # World frame velocities (direct from kinematics, no extra smoothing)
        self.vx = vx_body * cos_theta - vy_body * sin_theta
        self.vy = vx_body * sin_theta + vy_body * cos_theta
        self.omega = omega_body

        # Apply continuous friction/damping (always opposes motion)
        # This is a simple linear damping model: F_friction = -b * v
        # After integration: v_new = v * (1 - b * dt)
        friction_factor = 0.1  # Lower value = less friction, more responsive
        self.vx *= (1.0 - friction_factor * dt)
        self.vy *= (1.0 - friction_factor * dt)
        self.omega *= (1.0 - friction_factor * dt)

        # Integrate position (Euler integration)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.theta += self.omega * dt

        # Normalize theta to [-pi, pi]
        while self.theta > math.pi:
            self.theta -= 2 * math.pi
        while self.theta < -math.pi:
            self.theta += 2 * math.pi

    def get_position(self):
        """
        Get current robot position and orientation.

        Returns:
            (x, y, theta): Position in meters, orientation in radians
        """
        return self.x, self.y, self.theta

    def get_velocity(self):
        """
        Get current robot velocities.

        Returns:
            (vx, vy, omega): Linear velocities in m/s, angular in rad/s
        """
        return self.vx, self.vy, self.omega

    def get_radius(self):
        """Get robot radius for collision detection."""
        return self.radius

    def set_position(self, x, y, theta=None):
        """
        Set robot position (used for collision response or reset).

        Args:
            x: X position (meters)
            y: Y position (meters)
            theta: Optional orientation (radians)
        """
        self.x = x
        self.y = y
        if theta is not None:
            self.theta = theta

    def stop(self):
        """Stop all motors and velocities."""
        for wheel in self.target_speeds:
            self.target_speeds[wheel] = 0.0
            self.actual_speeds[wheel] = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.omega = 0.0

    def get_wheel_positions(self):
        """
        Get world positions of each wheel (for visualization).

        Returns:
            Dict of wheel positions: {"north": (x, y), ...}
        """
        cos_t = math.cos(self.theta)
        sin_t = math.sin(self.theta)
        r = self.radius

        # Wheel positions in body frame, then transformed to world
        # North: (0, +R) in body frame
        # South: (0, -R) in body frame
        # East: (+R, 0) in body frame
        # West: (-R, 0) in body frame

        positions = {
            "north": (
                self.x + 0 * cos_t - r * sin_t,
                self.y + 0 * sin_t + r * cos_t
            ),
            "south": (
                self.x + 0 * cos_t - (-r) * sin_t,
                self.y + 0 * sin_t + (-r) * cos_t
            ),
            "east": (
                self.x + r * cos_t - 0 * sin_t,
                self.y + r * sin_t + 0 * cos_t
            ),
            "west": (
                self.x + (-r) * cos_t - 0 * sin_t,
                self.y + (-r) * sin_t + 0 * cos_t
            ),
        }

        return positions

    def get_state_dict(self):
        """
        Get complete robot state as dictionary (for debugging/display).
        """
        return {
            "position": {"x": self.x, "y": self.y, "theta": self.theta},
            "velocity": {"vx": self.vx, "vy": self.vy, "omega": self.omega},
            "motors": {
                "target": self.target_speeds.copy(),
                "actual": self.actual_speeds.copy(),
            }
        }
