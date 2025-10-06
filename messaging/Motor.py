import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

socket.send_string("Hello from client!")
reply = socket.recv_string()
print(reply)