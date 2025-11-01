import pygame
import zmq
import json

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
# With a real simulation, we'll be updating motor speeds to move a robot here
message_text = "Waiting for messages..."
font = pygame.font.Font(None, 36)

running = True

#set up initial variables
bot_x = 400
bot_y = 300
speed = 0
direction = ""
yellow = (255, 255, 0)

while running:
    screen.fill((0, 0, 0))
    # Handle pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Check for ZMQ messages (non-blocking)
    try:
        message = socket.recv_string()
        command = json.loads(message)
        #read in commands from ZMQ message
        direction = command["command"]
        if "params" in command:
            if "speed" in command["params"]:
                speed = command["params"]["speed"]
        message_text = f"Received: {message}"
        socket.send_string("Message received!")  # Send reply
        print(f"Got message: {message}")
    except zmq.Again:
        # No message available, continue game loop
        pass
    
    # Render
    
    #execute command
    if direction == "forward":
        bot_y -= speed
    elif direction == "backward":
        bot_y += speed
    elif direction == "stop":
        speed = 0

    #redraw the bot in its new position
    bot = pygame.Rect(bot_x, bot_y, 10, 10)
    pygame.draw.rect(screen, yellow, bot)
    pygame.display.flip()
    
    clock.tick(60)  # 60 FPS

pygame.quit()
socket.close()
context.term()