import zmq
import json


# Sensor ID convention (matches Motor): 0=north, 1=south, 2=east, 3=west
ID_TO_WHEEL = {0: "north", 1: "south", 2: "east", 3: "west"}


class SensorBase:
    """
    Base class for sensor subscribers.
    Subscribes to one topic on the simulator's sensor PUB socket.
    """

    def __init__(self, topic, host="localhost", port=5557):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(f"tcp://{host}:{port}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        self.socket.setsockopt(zmq.RCVTIMEO, 0)  # Non-blocking
        self._latest = None

    def _drain(self):
        """Drain socket queue, keeping only the most recent payload."""
        while True:
            try:
                msg = self.socket.recv_string()
                _, payload = msg.split(" ", 1)
                self._latest = json.loads(payload)
            except zmq.Again:
                break

    def close(self):
        self.socket.close()
        self.context.term()
