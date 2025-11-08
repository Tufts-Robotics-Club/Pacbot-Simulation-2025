import pygame
import zmq
import initialize as my_maze
import string
from pprint import pprint

# Initialize pygame
pygame.init()
clock = pygame.time.Clock()

# initialize maze
width, height, maze = my_maze.initialize_simulation("/Users/jordangasaatura/Desktop/Pacbot-Simulation-2025/simulator/mazes/mini.json")

screen = pygame.display.set_mode((width*100, height*100))

# Set up ZeroMQ server (non-blocking)
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
socket.setsockopt(zmq.RCVTIMEO, 0)  # Non-blocking receives

# Game state
# With a real simulation, we'll be updating motor speeds to move a robot here
message_text = "Waiting for messages..."
font = pygame.font.Font(None, 36)

running = True
while running:
    # Handle pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Check for ZMQ messages (non-blocking)
    try:
        message = socket.recv_string()
        message_text = f"Received: {message}"
        socket.send_string("Message received!")  # Send reply
        print(f"Got message: {message}")
    except zmq.Again:
        # No message available, continue game loop
        pass
    
    # Render
    screen.fill((0, 0, 0))
    text_surface = font.render(message_text, True, (255, 255, 255))

    # zip does loop for two things at once
    # for every row in the maze, for every row_number 0 to height
    # then for every col in the row (row is an array),
    for row, row_number in zip(maze, range(height)):
        for col, col_number in zip(row, range(width)):
            if col == 1:
                square_color = (0, 0, 255)  # Blue
                square_x = row_number*100
                square_y = col_number*100
                square_size = 100
                #needs x and y coordinate, height and width of the square is square_size
                square_rect = pygame.Rect(square_y, square_x, square_size, square_size)
                pygame.draw.rect(screen, square_color, square_rect)

    pygame.display.flip()
    
    clock.tick(60)  # 60 FPS


pygame.quit()
socket.close()
context.term()