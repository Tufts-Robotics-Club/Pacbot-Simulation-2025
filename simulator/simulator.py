import pygame
import zmq
import initialize
# Initialize pygame
pygame.init()

width, height, layout = initialize.initialize_simulation("simulator/mazes/mini.json")
print("height: " + str(height))
print("width: " + str(width))


screen = pygame.display.set_mode((width * 100, height * 100))
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

    #maze 
    for row, rownumber in zip(layout, range(height)):
        #print(height)
        print(row)
        for col, colnumber in zip(row, range(width)):
            if col ==1:
                pygame.draw.rect(screen, (0, 0, 255), (colnumber*100, rownumber*100,100,100))
    print('end')


    pygame.display.flip()
    
    clock.tick(60)  # 60 FPS

pygame.quit()
socket.close()
context.term()