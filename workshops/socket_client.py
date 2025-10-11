# Socket Programming Workshop - Client
# William Soylemez - Robotics 2025

# This workshop covers basic network communication using ZMQ (ZeroMQ):
# - Connecting to a server
# - Sending messages
# - Receiving replies
# - Basic request-reply pattern

# SETUP: Make sure you have ZMQ installed!
# Run: pip install pyzmq

# INSTRUCTIONS:
# 1. Run socket_server.py FIRST in one terminal
# 2. Then run this file in another terminal
# 3. Type messages to send to the server
# 4. Type 'quit' to stop both programs

import zmq

print("=== Socket Client ===")
print("Connecting to server...")

# Create a ZMQ context
context = zmq.Context()

# Create a REQ (request) socket
socket = context.socket(zmq.REQ)

# Connect to the server on localhost port 5555
socket.connect("tcp://localhost:5555")

print("Connected to server on port 5555!")
print("Type your messages below (type 'quit' to exit):\n")

# ============================================
# TASK 1: Create the message loop
# ============================================
# TODO: Create a while loop that runs forever (while True:)


    # ============================================
    # TASK 2: Get user input
    # ============================================
    # TODO: Use input() to get a message from the user
    # Store it in a variable called 'message'
    
    
    # ============================================
    # TASK 3: Send the message to the server
    # ============================================
    # TODO: Send the message using socket.send_string()
    # Format: socket.send_string(message)
    
    
    # ============================================
    # TASK 4: Receive the server's reply
    # ============================================
    # TODO: Receive the reply using socket.recv_string()
    # Store it in a variable called 'reply'
    # Example: reply = socket.recv_string()
    
    
    # ============================================
    # TASK 5: Print the reply
    # ============================================
    # TODO: Print the reply from the server
    
    
    # Check if user wants to quit (if message.lower() == "quit")

# Clean up (this runs after the loop ends)
socket.close()
context.term()
print("Client stopped.")