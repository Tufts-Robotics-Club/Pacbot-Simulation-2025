import zmq
import json


class Motor:
    """
    Client-side motor interface. Identifies a motor by a single numeric ID
    (0=north, 1=south, 2=east, 3=west by convention — see simulator config).
    """

    def __init__(self, motor_id):
        self.motor_id = motor_id

        # Set up ZeroMQ client
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://localhost:5555")

    def _send_command(self, command, params=None):
        message = {"command": command, "id": self.motor_id}
        if params:
            message["params"] = params
        self.socket.send_string(json.dumps(message))
        reply = self.socket.recv_string()
        return reply

    def forward(self, speed):
        return self._send_command("move", {"speed": speed})

    def backward(self, speed):
        return self._send_command("move", {"speed": -speed})

    def stop(self):
        return self._send_command("move", {"speed": 0})

    def close(self):
        self.socket.close()
        self.context.term()
