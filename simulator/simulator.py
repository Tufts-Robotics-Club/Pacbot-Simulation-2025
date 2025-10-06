import pygame
import zmq

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Set up ZeroMQ server (non-blocking)
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
socket.setsockopt(zmq.RCVTIMEO, 0)  # Non-blocking receives

# Game state
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
    screen.blit(text_surface, (50, 50))
    pygame.display.flip()
    
    clock.tick(60)  # 60 FPS

pygame.quit()
socket.close()
context.term()