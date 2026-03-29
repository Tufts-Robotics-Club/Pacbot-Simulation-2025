"""
Collision detection for circular robot in grid-based maze.

Handles circle-rectangle collision detection and response.
"""

import math


def clamp(value, min_val, max_val):
    """Clamp a value to a range."""
    return max(min_val, min(max_val, value))


def circle_rect_collision(circle_x, circle_y, circle_radius,
                          rect_x, rect_y, rect_width, rect_height):
    """
    Check if a circle collides with an axis-aligned rectangle.

    Args:
        circle_x, circle_y: Center of circle
        circle_radius: Radius of circle
        rect_x, rect_y: Bottom-left corner of rectangle
        rect_width, rect_height: Dimensions of rectangle

    Returns:
        (collides, penetration_vector):
            collides: True if collision detected
            penetration_vector: (dx, dy) to push circle out, or None
    """
    # Find the closest point on the rectangle to the circle center
    closest_x = clamp(circle_x, rect_x, rect_x + rect_width)
    closest_y = clamp(circle_y, rect_y, rect_y + rect_height)

    # Calculate distance from circle center to closest point
    dx = circle_x - closest_x
    dy = circle_y - closest_y
    distance_sq = dx * dx + dy * dy

    # Check if distance is less than radius
    if distance_sq < circle_radius * circle_radius:
        # Collision detected
        distance = math.sqrt(distance_sq) if distance_sq > 0 else 0

        if distance > 0:
            # Normal case: calculate penetration vector
            penetration = circle_radius - distance
            # Normalize and scale by penetration depth
            nx = dx / distance
            ny = dy / distance
            return True, (nx * penetration, ny * penetration)
        else:
            # Circle center is inside rectangle - push out in nearest direction
            # Find which edge is closest
            dist_to_left = circle_x - rect_x
            dist_to_right = (rect_x + rect_width) - circle_x
            dist_to_bottom = circle_y - rect_y
            dist_to_top = (rect_y + rect_height) - circle_y

            min_dist = min(dist_to_left, dist_to_right, dist_to_bottom, dist_to_top)

            if min_dist == dist_to_left:
                return True, (-(circle_radius + dist_to_left), 0)
            elif min_dist == dist_to_right:
                return True, (circle_radius + dist_to_right, 0)
            elif min_dist == dist_to_bottom:
                return True, (0, -(circle_radius + dist_to_bottom))
            else:
                return True, (0, circle_radius + dist_to_top)

    return False, None


class CollisionHandler:
    """
    Handles collision detection between robot and maze walls.
    """

    def __init__(self, maze, cell_size=0.3):
        """
        Initialize collision handler.

        Args:
            maze: 2D list where 1=wall, 0=open
            cell_size: Size of each cell in meters
        """
        self.maze = maze
        self.cell_size = cell_size
        self.maze_height = len(maze)
        self.maze_width = len(maze[0]) if maze else 0

    def get_cell(self, x, y):
        """
        Get maze cell at world coordinates.

        Returns:
            Cell value (1=wall, 0=open) or 1 if out of bounds
        """
        cell_x = int(x / self.cell_size)
        cell_y = int(y / self.cell_size)

        # Treat out-of-bounds as walls
        if cell_x < 0 or cell_x >= self.maze_width:
            return 1
        if cell_y < 0 or cell_y >= self.maze_height:
            return 1

        return self.maze[cell_y][cell_x]

    def check_collision(self, robot_x, robot_y, robot_radius):
        """
        Check if robot collides with any maze walls.

        Args:
            robot_x, robot_y: Robot center position in world coordinates
            robot_radius: Robot radius in meters

        Returns:
            (collides, total_push):
                collides: True if any collision
                total_push: (dx, dy) vector to resolve all collisions
        """
        # Find range of cells the robot might overlap
        margin = robot_radius + 0.01  # Small margin for safety
        min_cell_x = int((robot_x - margin) / self.cell_size)
        max_cell_x = int((robot_x + margin) / self.cell_size)
        min_cell_y = int((robot_y - margin) / self.cell_size)
        max_cell_y = int((robot_y + margin) / self.cell_size)

        # Clamp to maze bounds
        min_cell_x = max(0, min_cell_x)
        max_cell_x = min(self.maze_width - 1, max_cell_x)
        min_cell_y = max(0, min_cell_y)
        max_cell_y = min(self.maze_height - 1, max_cell_y)

        total_push_x = 0.0
        total_push_y = 0.0
        any_collision = False

        # Check each potentially overlapping cell
        for cy in range(min_cell_y, max_cell_y + 1):
            for cx in range(min_cell_x, max_cell_x + 1):
                if self.maze[cy][cx] == 1:  # Wall cell
                    # Calculate cell rectangle in world coordinates
                    rect_x = cx * self.cell_size
                    rect_y = cy * self.cell_size

                    collides, push = circle_rect_collision(
                        robot_x, robot_y, robot_radius,
                        rect_x, rect_y, self.cell_size, self.cell_size
                    )

                    if collides:
                        any_collision = True
                        total_push_x += push[0]
                        total_push_y += push[1]

        # Also check boundaries (treat outside maze as walls)
        # Left boundary
        if robot_x - robot_radius < 0:
            any_collision = True
            total_push_x += robot_radius - robot_x
        # Right boundary
        if robot_x + robot_radius > self.maze_width * self.cell_size:
            any_collision = True
            total_push_x -= (robot_x + robot_radius) - self.maze_width * self.cell_size
        # Bottom boundary
        if robot_y - robot_radius < 0:
            any_collision = True
            total_push_y += robot_radius - robot_y
        # Top boundary
        if robot_y + robot_radius > self.maze_height * self.cell_size:
            any_collision = True
            total_push_y -= (robot_y + robot_radius) - self.maze_height * self.cell_size

        return any_collision, (total_push_x, total_push_y)

    def resolve_collision(self, robot, iterations=3):
        """
        Resolve collisions by pushing robot out of walls.

        Args:
            robot: Robot instance with get_position(), set_position(), get_radius()
            iterations: Number of resolution iterations (for corner cases)

        Returns:
            True if any collision was resolved
        """
        x, y, theta = robot.get_position()
        radius = robot.get_radius()

        any_resolved = False

        for _ in range(iterations):
            collides, push = self.check_collision(x, y, radius)

            if not collides:
                break

            any_resolved = True
            x += push[0]
            y += push[1]

        if any_resolved:
            robot.set_position(x, y)

            # Zero velocity components going into walls
            vx, vy, omega = robot.get_velocity()

            # Check which direction we pushed and zero that velocity component
            _, push = self.check_collision(x, y, radius)

            # If we had to push in a direction, the robot was moving into a wall
            # This is a simplification - more accurate would track which walls hit
            # For now, just apply some damping if collision occurred
            robot.vx *= 0.5
            robot.vy *= 0.5

        return any_resolved

    def find_valid_position(self, x, y, radius, search_radius=1.0):
        """
        Find nearest valid (non-colliding) position.

        Args:
            x, y: Desired position
            radius: Robot radius
            search_radius: Maximum search distance

        Returns:
            (valid_x, valid_y) or None if no valid position found
        """
        # First check if current position is valid
        collides, _ = self.check_collision(x, y, radius)
        if not collides:
            return x, y

        # Search in expanding circles
        for r in [0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0]:
            if r > search_radius:
                break

            # Try 8 directions
            for angle in range(0, 360, 45):
                test_x = x + r * math.cos(math.radians(angle))
                test_y = y + r * math.sin(math.radians(angle))

                collides, _ = self.check_collision(test_x, test_y, radius)
                if not collides:
                    return test_x, test_y

        return None

    def raycast(self, origin_x, origin_y, dir_x, dir_y, max_dist=2.0):
        """
        Cast a ray through the maze grid and return distance to nearest wall.

        Uses DDA (Digital Differential Analyzer) for accurate grid traversal.

        Args:
            origin_x, origin_y: Ray start position in world coordinates
            dir_x, dir_y: Ray direction (will be normalized)
            max_dist: Maximum raycast distance in meters

        Returns:
            Distance to nearest wall in meters, or max_dist if no wall hit
        """
        # Normalize direction
        length = math.sqrt(dir_x * dir_x + dir_y * dir_y)
        if length < 1e-10:
            return max_dist
        dir_x /= length
        dir_y /= length

        cs = self.cell_size

        # Check boundary hit distances
        # If ray would exit maze bounds, treat boundary as wall
        def boundary_dist():
            dists = []
            if dir_x > 0:
                dists.append((self.maze_width * cs - origin_x) / dir_x)
            elif dir_x < 0:
                dists.append(-origin_x / dir_x)
            if dir_y > 0:
                dists.append((self.maze_height * cs - origin_y) / dir_y)
            elif dir_y < 0:
                dists.append(-origin_y / dir_y)
            return min(dists) if dists else max_dist

        bound_dist = boundary_dist()

        # Current cell
        cell_x = int(origin_x / cs)
        cell_y = int(origin_y / cs)

        # If starting inside a wall, return 0
        if (0 <= cell_x < self.maze_width and 0 <= cell_y < self.maze_height
                and self.maze[cell_y][cell_x] == 1):
            return 0.0

        # DDA setup
        # Step direction
        step_x = 1 if dir_x >= 0 else -1
        step_y = 1 if dir_y >= 0 else -1

        # Distance along ray to cross one full cell in each axis
        delta_dist_x = abs(cs / dir_x) if abs(dir_x) > 1e-10 else 1e10
        delta_dist_y = abs(cs / dir_y) if abs(dir_y) > 1e-10 else 1e10

        # Distance from origin to the first cell boundary in each axis
        if dir_x >= 0:
            side_dist_x = ((cell_x + 1) * cs - origin_x) / dir_x if abs(dir_x) > 1e-10 else 1e10
        else:
            side_dist_x = (origin_x - cell_x * cs) / (-dir_x) if abs(dir_x) > 1e-10 else 1e10

        if dir_y >= 0:
            side_dist_y = ((cell_y + 1) * cs - origin_y) / dir_y if abs(dir_y) > 1e-10 else 1e10
        else:
            side_dist_y = (origin_y - cell_y * cs) / (-dir_y) if abs(dir_y) > 1e-10 else 1e10

        # Step through grid
        dist = 0.0
        while dist < max_dist:
            # Step to nearest cell boundary
            if side_dist_x < side_dist_y:
                dist = side_dist_x
                side_dist_x += delta_dist_x
                cell_x += step_x
            else:
                dist = side_dist_y
                side_dist_y += delta_dist_y
                cell_y += step_y

            if dist > max_dist:
                break

            # Check if out of bounds (boundary = wall)
            if cell_x < 0 or cell_x >= self.maze_width or cell_y < 0 or cell_y >= self.maze_height:
                return min(dist, bound_dist, max_dist)

            # Check if wall
            if self.maze[cell_y][cell_x] == 1:
                return dist

        return max_dist

    def get_maze_dimensions(self):
        """Get maze dimensions in world coordinates."""
        return (
            self.maze_width * self.cell_size,
            self.maze_height * self.cell_size
        )
