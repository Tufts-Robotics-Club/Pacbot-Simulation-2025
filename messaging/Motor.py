import zmq
import json

# Goal is to have same interface as GPIO PhaseEnableMotor
# May change if using different library in real motor module
class PhaseEnableMotor: 
    def __init__(self, pin1, pin2):
        self.pin1 = pin1
        self.pin2 = pin2 # Pins are just an identifier here
        
        # Set up ZeroMQ client
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5555")
        

    def _send_command(self, command, params=None):
        message = {"command": command, "pin1": self.pin1, "pin2": self.pin2}
        if params:
            message["params"] = params
        self.socket.send_string(json.dumps(message))
        reply = self.socket.recv_string()
        return reply

    def forward(self, speed):
        return self._send_command("forward", {"speed": speed})

    def backward(self, speed):
        return self._send_command("backward", {"speed": speed})

    def stop(self):
        return self._send_command("stop")

    def close(self):
        self.socket.close()
        self.context.term()