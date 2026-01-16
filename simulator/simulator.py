"""
Pacbot Simulator - Main simulation loop with robot physics.

Receives motor commands via ZeroMQ and simulates robot movement.
"""

import pygame
import zmq
import json
import time
import math
from robot import Robot

# Initialize pygame
pygame.init()
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pacbot Simulator")
clock = pygame.time.Clock()

# Set up ZeroMQ server (non-blocking)
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
socket.setsockopt(zmq.RCVTIMEO, 0)  # Non-blocking receives

# Motor pin configuration - maps (pin1, pin2) tuples to wheel positions
MOTOR_PIN_CONFIG = {
    (17, 27): "north",
    (22, 23): "south",
    (24, 25): "east",
    (5, 6): "west",
}

# Simulation area (meters) - robot moves in this space
SIM_WIDTH = 2.0   # 2 meters wide
SIM_HEIGHT = 2.0  # 2 meters tall

# Display settings
SIM_DISPLAY_X = 50  # Simulation view left edge
SIM_DISPLAY_Y = 50  # Simulation view top edge
SIM_DISPLAY_WIDTH = 500
SIM_DISPLAY_HEIGHT = 500
PIXELS_PER_METER = SIM_DISPLAY_WIDTH / SIM_WIDTH

# Colors
COLOR_BG = (30, 30, 30)
COLOR_SIM_BG = (20, 20, 40)
COLOR_SIM_BORDER = (60, 60, 80)
COLOR_GRID = (40, 40, 60)
COLOR_ROBOT = (255, 220, 50)  # Yellow
COLOR_ROBOT_OUTLINE = (200, 170, 30)
COLOR_DIRECTION = (255, 100, 100)
COLOR_WHEEL_STOPPED = (80, 80, 80)
COLOR_WHEEL_FORWARD = (50, 200, 50)
COLOR_WHEEL_BACKWARD = (200, 50, 50)
COLOR_VELOCITY = (100, 200, 255)
COLOR_TEXT = (200, 200, 200)
COLOR_LABEL = (150, 150, 150)

# Fonts
font_large = pygame.font.Font(None, 42)
font_medium = pygame.font.Font(None, 28)
font_small = pygame.font.Font(None, 22)

# Create robot at center of simulation area
robot = Robot(x=SIM_WIDTH/2, y=SIM_HEIGHT/2, theta=math.pi/2)  # Facing up

# Message display
last_command = "None"

# Physics timing
PHYSICS_DT = 0.01  # 100 Hz physics
physics_accumulator = 0.0
last_physics_time = time.time()


def get_wheel_position(pin1, pin2):
    """Look up which wheel corresponds to the given pin pair."""
    key = (pin1, pin2)
    if key in MOTOR_PIN_CONFIG:
        return MOTOR_PIN_CONFIG[key]
    key_rev = (pin2, pin1)
    if key_rev in MOTOR_PIN_CONFIG:
        return MOTOR_PIN_CONFIG[key_rev]
    return None


def handle_motor_command(message_data):
    """Handle incoming motor commands from PhaseEnableMotor instances."""
    global last_command

    command = message_data.get("command", "unknown")
    pin1 = message_data.get("pin1")
    pin2 = message_data.get("pin2")
    params = message_data.get("params", {})

    wheel = get_wheel_position(pin1, pin2)

    response = {
        "status": "ok",
        "command": command,
        "pin1": pin1,
        "pin2": pin2,
        "wheel": wheel
    }

    if wheel is None:
        response["status"] = "warning"
        response["message"] = f"Unknown motor pins ({pin1}, {pin2})"
        last_command = f"WARNING: Unknown pins ({pin1}, {pin2})"
        return response

    if command == "move":
        # Unified move command: positive speed = forward, negative = backward, 0 = stop
        speed = params.get("speed", 0.0)
        speed = max(-1.0, min(1.0, float(speed)))
        robot.set_motor_speed(wheel, speed)

        if abs(speed) < 0.01:
            last_command = f"{wheel.upper()}: STOP"
            response["message"] = f"{wheel} stopped"
        elif speed > 0:
            last_command = f"{wheel.upper()}: fwd {speed:.2f}"
            response["message"] = f"{wheel} forward at {speed}"
        else:
            last_command = f"{wheel.upper()}: bwd {abs(speed):.2f}"
            response["message"] = f"{wheel} backward at {abs(speed)}"

    # Legacy commands for backwards compatibility
    elif command == "forward":
        speed = params.get("speed", 0.0)
        speed = max(0.0, min(1.0, float(speed)))
        robot.set_motor_speed(wheel, speed)
        last_command = f"{wheel.upper()}: fwd {speed:.2f}"
        response["message"] = f"{wheel} forward at {speed}"

    elif command == "backward":
        speed = params.get("speed", 0.0)
        speed = max(0.0, min(1.0, float(speed)))
        robot.set_motor_speed(wheel, -speed)
        last_command = f"{wheel.upper()}: bwd {speed:.2f}"
        response["message"] = f"{wheel} backward at {speed}"

    elif command == "stop":
        robot.set_motor_speed(wheel, 0.0)
        last_command = f"{wheel.upper()}: STOP"
        response["message"] = f"{wheel} stopped"

    else:
        response["status"] = "error"
        response["message"] = f"Unknown command: {command}"
        last_command = f"ERROR: Unknown '{command}'"

    return response


def world_to_screen(x, y):
    """Convert world coordinates (meters) to screen pixels."""
    screen_x = SIM_DISPLAY_X + x * PIXELS_PER_METER
    screen_y = SIM_DISPLAY_Y + SIM_DISPLAY_HEIGHT - y * PIXELS_PER_METER  # Flip Y
    return int(screen_x), int(screen_y)


def meters_to_pixels(meters):
    """Convert a distance in meters to pixels."""
    return int(meters * PIXELS_PER_METER)


def get_wheel_color(speed):
    """Get wheel color based on speed."""
    if abs(speed) < 0.01:
        return COLOR_WHEEL_STOPPED
    elif speed > 0:
        intensity = int(100 + 155 * min(1.0, abs(speed)))
        return (0, intensity, 0)
    else:
        intensity = int(100 + 155 * min(1.0, abs(speed)))
        return (intensity, 0, 0)


def draw_simulation_area():
    """Draw the simulation area with grid."""
    # Background
    pygame.draw.rect(screen, COLOR_SIM_BG,
                    (SIM_DISPLAY_X, SIM_DISPLAY_Y, SIM_DISPLAY_WIDTH, SIM_DISPLAY_HEIGHT))

    # Grid lines (every 0.25 meters)
    grid_spacing = 0.25
    for x in range(int(SIM_WIDTH / grid_spacing) + 1):
        sx = SIM_DISPLAY_X + int(x * grid_spacing * PIXELS_PER_METER)
        pygame.draw.line(screen, COLOR_GRID,
                        (sx, SIM_DISPLAY_Y),
                        (sx, SIM_DISPLAY_Y + SIM_DISPLAY_HEIGHT), 1)
    for y in range(int(SIM_HEIGHT / grid_spacing) + 1):
        sy = SIM_DISPLAY_Y + SIM_DISPLAY_HEIGHT - int(y * grid_spacing * PIXELS_PER_METER)
        pygame.draw.line(screen, COLOR_GRID,
                        (SIM_DISPLAY_X, sy),
                        (SIM_DISPLAY_X + SIM_DISPLAY_WIDTH, sy), 1)

    # Border
    pygame.draw.rect(screen, COLOR_SIM_BORDER,
                    (SIM_DISPLAY_X, SIM_DISPLAY_Y, SIM_DISPLAY_WIDTH, SIM_DISPLAY_HEIGHT), 2)

    # Axis labels
    label = font_small.render("0", True, COLOR_LABEL)
    screen.blit(label, (SIM_DISPLAY_X - 15, SIM_DISPLAY_Y + SIM_DISPLAY_HEIGHT + 5))

    label = font_small.render(f"{SIM_WIDTH}m", True, COLOR_LABEL)
    screen.blit(label, (SIM_DISPLAY_X + SIM_DISPLAY_WIDTH - 20, SIM_DISPLAY_Y + SIM_DISPLAY_HEIGHT + 5))

    label = font_small.render(f"{SIM_HEIGHT}m", True, COLOR_LABEL)
    screen.blit(label, (SIM_DISPLAY_X - 35, SIM_DISPLAY_Y - 5))


def draw_robot():
    """Draw the robot in the simulation area."""
    x, y, theta = robot.get_position()

    # Convert to screen coordinates
    sx, sy = world_to_screen(x, y)
    radius_px = meters_to_pixels(robot.radius)

    # Draw robot body (circle)
    pygame.draw.circle(screen, COLOR_ROBOT, (sx, sy), radius_px)
    pygame.draw.circle(screen, COLOR_ROBOT_OUTLINE, (sx, sy), radius_px, 2)

    # Draw direction indicator (triangle pointing forward)
    # Forward is +Y in body frame, which is the direction of theta
    dir_length = radius_px * 0.7
    dir_x = sx + dir_length * math.cos(theta)
    dir_y = sy - dir_length * math.sin(theta)  # Flip Y for screen

    # Triangle pointing in direction of travel
    angle_spread = 0.4
    p1 = (dir_x, dir_y)
    p2 = (sx + radius_px * 0.3 * math.cos(theta + math.pi - angle_spread),
          sy - radius_px * 0.3 * math.sin(theta + math.pi - angle_spread))
    p3 = (sx + radius_px * 0.3 * math.cos(theta + math.pi + angle_spread),
          sy - radius_px * 0.3 * math.sin(theta + math.pi + angle_spread))
    pygame.draw.polygon(screen, COLOR_DIRECTION, [p1, p2, p3])

    # Draw wheels
    wheel_length = meters_to_pixels(0.03)  # 3cm wheels
    wheel_width = 4

    wheel_positions = robot.get_wheel_positions()
    wheel_angles = {
        "north": theta + math.pi/2,  # Perpendicular to radius (horizontal in body)
        "south": theta + math.pi/2,
        "east": theta,  # Along radius direction (vertical in body)
        "west": theta,
    }

    for wheel_name, (wx, wy) in wheel_positions.items():
        wsx, wsy = world_to_screen(wx, wy)
        speed = robot.get_motor_speed(wheel_name)
        color = get_wheel_color(speed)
        angle = wheel_angles[wheel_name]

        # Draw wheel as rotated rectangle
        dx = math.cos(angle) * wheel_length / 2
        dy = -math.sin(angle) * wheel_length / 2  # Flip Y
        wx1 = math.cos(angle + math.pi/2) * wheel_width / 2
        wy1 = -math.sin(angle + math.pi/2) * wheel_width / 2

        points = [
            (wsx - dx + wx1, wsy - dy + wy1),
            (wsx + dx + wx1, wsy + dy + wy1),
            (wsx + dx - wx1, wsy + dy - wy1),
            (wsx - dx - wx1, wsy - dy - wy1),
        ]
        pygame.draw.polygon(screen, color, points)

    # Draw velocity vector
    vx, vy, _ = robot.get_velocity()
    speed = math.sqrt(vx*vx + vy*vy)
    if speed > 0.01:
        # Scale velocity for display (50 pixels per m/s)
        vel_scale = 100
        vel_ex = sx + vx * vel_scale
        vel_ey = sy - vy * vel_scale  # Flip Y
        pygame.draw.line(screen, COLOR_VELOCITY, (sx, sy), (vel_ex, vel_ey), 2)
        # Arrowhead
        pygame.draw.circle(screen, COLOR_VELOCITY, (int(vel_ex), int(vel_ey)), 4)


def draw_info_panel():
    """Draw information panel on the right side."""
    panel_x = SIM_DISPLAY_X + SIM_DISPLAY_WIDTH + 30
    y = 50

    # Title
    title = font_large.render("Pacbot Simulator", True, (255, 255, 100))
    screen.blit(title, (panel_x, y))
    y += 45

    # Status
    status = font_small.render(f"Last: {last_command}", True, (100, 255, 100))
    screen.blit(status, (panel_x, y))
    y += 30

    # Position
    px, py, theta = robot.get_position()
    pos_label = font_medium.render("Position:", True, COLOR_TEXT)
    screen.blit(pos_label, (panel_x, y))
    y += 25

    pos_text = font_small.render(f"  x: {px:.3f} m", True, COLOR_LABEL)
    screen.blit(pos_text, (panel_x, y))
    y += 20
    pos_text = font_small.render(f"  y: {py:.3f} m", True, COLOR_LABEL)
    screen.blit(pos_text, (panel_x, y))
    y += 20
    pos_text = font_small.render(f"  θ: {math.degrees(theta):.1f}°", True, COLOR_LABEL)
    screen.blit(pos_text, (panel_x, y))
    y += 30

    # Velocity
    vx, vy, omega = robot.get_velocity()
    vel_label = font_medium.render("Velocity:", True, COLOR_TEXT)
    screen.blit(vel_label, (panel_x, y))
    y += 25

    speed = math.sqrt(vx*vx + vy*vy)
    vel_text = font_small.render(f"  speed: {speed:.3f} m/s", True, COLOR_LABEL)
    screen.blit(vel_text, (panel_x, y))
    y += 20
    vel_text = font_small.render(f"  ω: {math.degrees(omega):.1f}°/s", True, COLOR_LABEL)
    screen.blit(vel_text, (panel_x, y))
    y += 30

    # Motor speeds
    motor_label = font_medium.render("Motors:", True, COLOR_TEXT)
    screen.blit(motor_label, (panel_x, y))
    y += 25

    for wheel in ["north", "south", "east", "west"]:
        actual = robot.actual_speeds[wheel]
        color = get_wheel_color(actual)

        # Draw mini speed bar
        bar_width = 80
        bar_height = 12
        bar_x = panel_x + 60

        # Background
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, y, bar_width, bar_height))

        # Speed fill
        if actual != 0:
            fill_width = int(abs(actual) * bar_width / 2)
            if actual > 0:
                pygame.draw.rect(screen, color, (bar_x + bar_width//2, y, fill_width, bar_height))
            else:
                pygame.draw.rect(screen, color, (bar_x + bar_width//2 - fill_width, y, fill_width, bar_height))

        # Center line
        pygame.draw.line(screen, (100, 100, 100),
                        (bar_x + bar_width//2, y),
                        (bar_x + bar_width//2, y + bar_height), 1)

        # Label
        label = font_small.render(f"{wheel[0].upper()}", True, COLOR_LABEL)
        screen.blit(label, (panel_x, y))

        # Value
        val = font_small.render(f"{actual:+.2f}", True, COLOR_LABEL)
        screen.blit(val, (bar_x + bar_width + 5, y))

        y += 20

    y += 20

    # Instructions
    instructions = [
        "Controls:",
        "  R - Reset position",
        "  SPACE - Stop all motors",
        "  ESC - Quit",
    ]
    for line in instructions:
        text = font_small.render(line, True, (100, 100, 150))
        screen.blit(text, (panel_x, y))
        y += 18


def draw_fps(fps):
    """Draw FPS counter."""
    fps_text = font_small.render(f"FPS: {fps}", True, COLOR_LABEL)
    screen.blit(fps_text, (WINDOW_WIDTH - 70, 10))


# Main loop
running = True
fps_counter = 0
fps_timer = time.time()
current_fps = 0

print("=" * 60)
print("Pacbot Simulator Started")
print("=" * 60)
print(f"Robot starting at ({robot.x:.2f}, {robot.y:.2f})")
print(f"Motor pin configuration:")
for pins, wheel in MOTOR_PIN_CONFIG.items():
    print(f"  Pins {pins} -> {wheel} wheel")
print("=" * 60)

while running:
    # Calculate frame time
    current_time = time.time()
    frame_time = current_time - last_physics_time
    last_physics_time = current_time
    physics_accumulator += frame_time

    # Handle pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                # Reset robot position
                robot.set_position(SIM_WIDTH/2, SIM_HEIGHT/2, math.pi/2)
                robot.stop()
                last_command = "RESET (keyboard)"
            elif event.key == pygame.K_SPACE:
                # Stop all motors
                robot.stop()
                last_command = "STOP ALL (keyboard)"

    # Check for ZMQ messages (non-blocking)
    try:
        message_str = socket.recv_string()
        try:
            message_data = json.loads(message_str)
            response = handle_motor_command(message_data)
            socket.send_string(json.dumps(response))
        except json.JSONDecodeError:
            socket.send_string(json.dumps({"status": "error", "message": "Invalid JSON"}))
    except zmq.Again:
        pass

    # Fixed timestep physics updates
    while physics_accumulator >= PHYSICS_DT:
        robot.update(PHYSICS_DT)

        # Keep robot in bounds (simple boundary collision)
        x, y, theta = robot.get_position()
        r = robot.radius
        clamped = False

        if x - r < 0:
            x = r
            robot.vx = max(0, robot.vx)
            clamped = True
        elif x + r > SIM_WIDTH:
            x = SIM_WIDTH - r
            robot.vx = min(0, robot.vx)
            clamped = True

        if y - r < 0:
            y = r
            robot.vy = max(0, robot.vy)
            clamped = True
        elif y + r > SIM_HEIGHT:
            y = SIM_HEIGHT - r
            robot.vy = min(0, robot.vy)
            clamped = True

        if clamped:
            robot.set_position(x, y)

        physics_accumulator -= PHYSICS_DT

    # FPS calculation
    fps_counter += 1
    if current_time - fps_timer >= 1.0:
        current_fps = fps_counter
        fps_counter = 0
        fps_timer = current_time

    # Render
    screen.fill(COLOR_BG)
    draw_simulation_area()
    draw_robot()
    draw_info_panel()
    draw_fps(current_fps)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
socket.close()
context.term()
print("\nSimulator closed.")
