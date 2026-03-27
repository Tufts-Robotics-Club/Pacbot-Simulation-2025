import zmq
import json


class SensorSubscriber:
    def __init__(self, host="localhost", port=5556):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(f"tcp://{host}:{port}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "sensors")
        self.socket.setsockopt(zmq.RCVTIMEO, 0)  # Non-blocking

    def _recv(self):
        """Receive one message, return parsed data or None."""
        try:
            msg = self.socket.recv_string()
            # Strip topic prefix ("sensors ")
            payload = msg.split(" ", 1)[1]
            return json.loads(payload)
        except zmq.Again:
            return None

    def get_position(self):
        """Return latest (x, y, theta) or None if no data available."""
        data = self.get_latest()
        if data is None:
            return None
        return (data["x"], data["y"], data["theta"])

    def get_latest(self):
        """Drain queue and return the most recent message dict, or None."""
        latest = None
        while True:
            msg = self._recv()
            if msg is None:
                break
            latest = msg
        return latest

    def close(self):
        self.socket.close()
        self.context.term()
