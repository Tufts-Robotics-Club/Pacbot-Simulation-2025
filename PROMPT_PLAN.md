# Pacbot Simulator Completion Plan

## Project Overview
Complete a physically accurate pygame-based simulator for a circular four-wheel omniwheel pacbot robot. The simulator receives **low-level motor commands** via ZeroMQ (using the existing `PhaseEnableMotor` interface) and calculates robot physics internally.

## Robot Design

### Physical Configuration
```
           N (wheel)
            ═══
             │
    W ║──────●──────║ E
      ║      │      ║
            ═══
           S (wheel)

- Circular body with 4 omniwheels
- Wheels positioned at N, S, E, W poles (tangent to circle)
- North/South wheels: horizontal, control left/right (strafe)
- East/West wheels: vertical, control forward/back
- All wheels rotating same direction = rotation
```

### Kinematics
- **Forward motion**: East + West wheels forward (same direction)
- **Backward motion**: East + West wheels backward
- **Strafe left**: North forward + South backward
- **Strafe right**: North backward + South forward
- **Rotate CW**: All wheels forward
- **Rotate CCW**: All wheels backward
- **Diagonal**: Combination of the above

---

## Current State Analysis

### What Exists (After Phase 1)
- **Motor.py**: `PhaseEnableMotor` class with forward/backward/stop commands
- **simulator.py**: Pygame window with ZeroMQ server, tracks 4 motors by pin ID
- **test_omniwheel.py**: Test script using 4 separate motor instances
- **initialize.py**: Maze loading from JSON
- **mini.json**: 5x5 test maze (walls=1, open=0)

### Architecture
```
┌─────────────────────┐     ZeroMQ      ┌─────────────────────┐
│   Control Code      │ ───────────────▶│     Simulator       │
├─────────────────────┤    (port 5555)  ├─────────────────────┤
│ PhaseEnableMotor(N) │                 │ - Receives commands │
│ PhaseEnableMotor(S) │    forward()    │ - Maps pins→wheels  │
│ PhaseEnableMotor(E) │    backward()   │ - Calculates physics│
│ PhaseEnableMotor(W) │    stop()       │ - Renders robot     │
└─────────────────────┘                 └─────────────────────┘
```

### What's Missing
- Robot physics model (convert motor speeds → robot motion)
- Collision detection with maze walls
- Maze rendering
- Robot visualization in maze
- Sensor simulation (encoders, IMU, distance sensors)

---

## Implementation Plan

### Phase 1: Motor Interface ✓ COMPLETE

The existing `PhaseEnableMotor` interface is preserved:
- 4 separate motor objects, one per wheel
- Each identified by (pin1, pin2) tuple
- Commands: `forward(speed)`, `backward(speed)`, `stop()`
- Simulator maps pin pairs to wheel positions (N/S/E/W)

---

### Phase 2: Robot Physics Model

**Objective**: Simulate how motor speeds translate to robot motion

**Tasks**:
1. **Create `simulator/robot.py`**:
   - Robot state: position (x, y), orientation (theta)
   - Current velocities: (vx, vy, omega)
   - Physical parameters:
     - Radius: 0.075m (7.5cm radius, 15cm diameter)
     - Mass: 1.5 kg
     - Moment of inertia: I = 0.5 * m * r² (solid disk)
     - Wheel radius: 0.025m (2.5cm)
     - Max wheel speed: 1.0 (normalized, maps to ~0.3 m/s tangential)

2. **Forward Kinematics** (motor speeds → robot velocity):
   ```python
   # Given motor speeds: n, s, e, w (range -1 to +1)
   # Each wheel contributes force tangent to the circle

   # North wheel at (0, +R): pushes in ±X direction
   # South wheel at (0, -R): pushes in ±X direction
   # East wheel at (+R, 0): pushes in ±Y direction
   # West wheel at (-R, 0): pushes in ±Y direction

   # Linear velocity (in robot frame):
   # vx (forward) = wheel_radius * (e + w) / 2 * max_speed
   # vy (strafe)  = wheel_radius * (n - s) / 2 * max_speed

   # Note: For strafe, n and s push opposite directions
   # n forward + s backward = strafe left (positive vy)

   # Angular velocity:
   # All wheels tangent to circle, so all contribute to rotation
   # omega = wheel_radius * (n + s + e + w) / (4 * R) * max_speed
   ```

3. **Physics Integration**:
   ```python
   # Motor response (first-order lag)
   tau = 0.05  # 50ms time constant
   actual_speed += (target_speed - actual_speed) * dt / tau

   # Calculate robot velocity from wheel speeds
   vx_local = calculate_vx(wheel_speeds)
   vy_local = calculate_vy(wheel_speeds)
   omega = calculate_omega(wheel_speeds)

   # Apply damping (friction)
   damping = 0.1
   vx_local *= (1 - damping * dt)
   vy_local *= (1 - damping * dt)
   omega *= (1 - damping * dt)

   # Transform to world frame and integrate
   vx_world = vx_local * cos(theta) - vy_local * sin(theta)
   vy_world = vx_local * sin(theta) + vy_local * cos(theta)

   x += vx_world * dt
   y += vy_world * dt
   theta += omega * dt
   ```

4. **Robot class interface**:
   ```python
   class Robot:
       def set_motor_speed(self, wheel: str, speed: float)
       def update(self, dt: float)  # Physics step
       def get_position(self) -> Tuple[float, float, float]  # x, y, theta
       def get_velocity(self) -> Tuple[float, float, float]  # vx, vy, omega
       def get_radius(self) -> float  # For collision
   ```

**Expected outcome**: Robot moves realistically based on motor commands

---

### Phase 3: Collision Detection

**Objective**: Prevent robot from passing through walls

**Tasks**:
1. **Create `simulator/collision.py`**:
   - Grid-based collision (efficient for maze)
   - Cell size configurable (default: 0.3m per cell)
   - Robot treated as circle (radius = 0.075m)

2. **Collision algorithm**:
   ```python
   def check_collision(robot_x, robot_y, robot_radius, maze, cell_size):
       # Find cells the robot overlaps
       min_cell_x = int((robot_x - robot_radius) / cell_size)
       max_cell_x = int((robot_x + robot_radius) / cell_size)
       min_cell_y = int((robot_y - robot_radius) / cell_size)
       max_cell_y = int((robot_y + robot_radius) / cell_size)

       # Check each overlapped cell
       for cx in range(min_cell_x, max_cell_x + 1):
           for cy in range(min_cell_y, max_cell_y + 1):
               if maze[cy][cx] == 1:  # Wall
                   # Circle-rectangle collision
                   if circle_rect_collision(robot_x, robot_y, robot_radius,
                                           cx * cell_size, cy * cell_size, cell_size):
                       return True, (cx, cy)
       return False, None
   ```

3. **Collision response**:
   - Push robot out of wall (find nearest valid position)
   - Zero velocity component into wall
   - Allow sliding along walls

**Expected outcome**: Robot stops at walls, can slide along them

---

### Phase 4: Maze Rendering

**Objective**: Visualize the maze environment

**Tasks**:
1. **Maze visualization**:
   - Load maze from JSON
   - Draw walls as filled rectangles
   - Draw paths as different color
   - Scale: configurable pixels per cell

2. **Rendering parameters**:
   ```python
   CELL_SIZE_PIXELS = 40  # 40 pixels per maze cell
   WALL_COLOR = (30, 30, 60)
   PATH_COLOR = (20, 20, 30)
   GRID_COLOR = (40, 40, 50)
   ```

3. **Coordinate transformation**:
   ```python
   def world_to_screen(x, y, maze_height, cell_size_pixels, cell_size_meters):
       screen_x = x / cell_size_meters * cell_size_pixels
       screen_y = (maze_height - y / cell_size_meters) * cell_size_pixels  # Flip Y
       return screen_x, screen_y
   ```

**Expected outcome**: Clear maze visualization

---

### Phase 5: Robot Rendering

**Objective**: Visualize the circular robot in the maze

**Tasks**:
1. **Robot body**:
   - Draw as circle (yellow, like pacman)
   - Size matches robot radius scaled to pixels
   - Direction indicator (triangle or wedge)

2. **Wheel visualization**:
   - 4 rectangles at N/S/E/W positions
   - Color indicates speed/direction:
     - Green = forward
     - Red = backward
     - Gray = stopped
   - Intensity indicates speed magnitude

3. **Additional overlays** (toggle with keys):
   - Velocity vector
   - Collision boundary
   - Position/orientation text

**Expected outcome**: Robot clearly visible with orientation

---

### Phase 6: Sensor Simulation

**Objective**: Provide sensor data for control algorithms

**Tasks**:
1. **Wheel Encoders**:
   - Track cumulative rotation per wheel
   - Resolution: 1000 ticks/revolution
   - Add noise: ±0.5% Gaussian

2. **IMU**:
   - Gyroscope: angular velocity (omega)
   - Accelerometer: linear acceleration
   - Add realistic noise and drift

3. **Distance Sensors**:
   - Ray-cast from robot perimeter
   - 4-8 sensors around robot
   - Range: 5cm to 100cm
   - Add noise: ±1cm

4. **Sensor query protocol**:
   - New command type in PhaseEnableMotor (or separate interface)
   - Returns JSON with all sensor data
   - Alternative: Include in motor command responses

**Expected outcome**: Realistic sensor data for testing

---

### Phase 7: Integration

**Objective**: Combine all systems into working simulator

**Tasks**:
1. **Main loop structure**:
   ```python
   physics_dt = 0.01  # 100 Hz
   accumulator = 0.0

   while running:
       frame_time = clock.tick(60) / 1000.0
       accumulator += frame_time

       # Handle ZeroMQ messages
       process_motor_commands()

       # Fixed timestep physics
       while accumulator >= physics_dt:
           robot.update(physics_dt)
           handle_collisions()
           sensors.update(physics_dt)
           accumulator -= physics_dt

       # Render
       draw_maze()
       draw_robot()
       draw_ui()
       pygame.display.flip()
   ```

2. **Configuration file** (`simulator/config.py`):
   - Robot parameters (radius, mass, max speed)
   - Physics parameters (damping, motor lag)
   - Display settings
   - Pin-to-wheel mapping

**Expected outcome**: Fully integrated simulator

---

### Phase 8: Testing and Calibration

**Tasks**:
1. **Motion tests**:
   - Forward: E+W forward → robot moves +Y
   - Strafe: N forward, S backward → robot moves +X
   - Rotate: All forward → robot spins CW

2. **Collision tests**:
   - Robot stops at walls
   - Can slide along walls
   - No wall penetration

3. **Sensor tests**:
   - Encoders accumulate correctly
   - Distance sensors return accurate values
   - IMU matches actual motion

---

### Phase 9: Documentation

**Tasks**:
1. Update README with usage instructions
2. Document pin configuration
3. Create example control scripts
4. Add additional test mazes

---

## Key Formulas

### Omniwheel Kinematics (Circular Robot, N/S/E/W Configuration)

Given motor speeds: `n`, `s`, `e`, `w` (normalized -1 to +1)

**Robot Velocity (local frame)**:
```
vx = k * (e + w)           # Forward/back from E/W wheels
vy = k * (s - n)           # Strafe from N/S wheels (note: s-n for positive = right)
omega = k * (n + s + e + w) / R   # All wheels contribute to rotation
```
Where `k = wheel_radius * max_tangential_speed / 2`

**Direction Convention**:
- Robot faces "north" (up on screen) at theta = π/2
- theta = 0 means facing right (+X world)
- Positive omega = counter-clockwise rotation

---

## File Structure (Target)

```
Pacbot-Simulation-2025/
├── messaging/
│   ├── Motor.py              # PhaseEnableMotor class (unchanged)
│   ├── test_motors.py        # Original test
│   └── test_omniwheel.py     # 4-wheel test script
├── simulator/
│   ├── simulator.py          # Main simulator (to be updated)
│   ├── robot.py              # Robot physics (Phase 2)
│   ├── collision.py          # Collision detection (Phase 3)
│   ├── sensors.py            # Sensor simulation (Phase 6)
│   ├── config.py             # Configuration (Phase 7)
│   ├── initialize.py         # Maze loading (exists)
│   └── mazes/
│       ├── mini.json         # 5x5 test maze
│       ├── empty.json        # Empty arena for testing
│       └── pacman.json       # Full pacman layout
├── tests/
│   ├── test_kinematics.py
│   ├── test_collision.py
│   └── test_sensors.py
├── PROMPT_PLAN.md            # This file
├── README.md
└── requirements.txt
```

---

## Success Criteria

1. Robot moves correctly based on motor commands
2. Kinematics match expected behavior (forward, strafe, rotate, diagonal)
3. Collisions prevent wall penetration
4. Sensors provide realistic data
5. 60 FPS rendering, 100 Hz physics
6. Control code uses same Motor interface as real robot

---

## Notes

- **No high-level velocity commands**: The control code only has access to `forward()`, `backward()`, and `stop()` for each motor
- **Simulator does the physics**: All kinematics calculations happen inside the simulator
- **Pin identification**: Motors are identified by (pin1, pin2) tuples, mapped to wheel positions in simulator config
- **Circular robot**: Simplifies collision detection (circle-rectangle) and kinematics
