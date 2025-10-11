# Socket Programming Workshop - Server
# William Soylemez - Robotics 2025

# This is the SERVER file - it listens for messages and prints them
# Run this file FIRST before running the client!

import zmq

print("=== Socket Server ===")
print("Starting server...")

# Create a ZMQ context
context = zmq.Context()

# Create a REP (reply) socket
socket = context.socket(zmq.REP)

# Bind to port 5555 on localhost
socket.bind("tcp://*:5555")

print("Server is listening on port 5555...")
print("Waiting for messages from client...\n")

# Server loop - run forever
while True:
    # Wait for a message from the client
    message = socket.recv_string()
    
    # Print the received message
    print(f"Received from client: {message}")
    
    # Send a reply back to the client
    socket.send_string("Message received!")
    
    # If client sends "quit", stop the server
    if message.lower() == "quit":
        print("\nClient sent 'quit'. Shutting down server...")
        break

# Clean up
socket.close()
context.term()
print("Server stopped.")