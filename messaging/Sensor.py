import zmq
import json


class SensorSubscriber:
    def __init__(self, host="localhost", port=5557):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(f"tcp://{host}:{port}")
        self.socket.setsockopt_string(zmq.SUBSCRIBE, "sensors")
        self.socket.setsockopt(zmq.RCVTIMEO, 0)  # Non-blocking

        self._latest = {"tof": None, "encoders": None, "imu": None}

    def _drain(self):
        """Drain the socket queue, routing messages to the appropriate slot."""
        while True:
            try:
                msg = self.socket.recv_string()
                topic, payload = msg.split(" ", 1)
                key = topic.split(".")[-1]  # "tof", "encoders", or "imu"
                if key in self._latest:
                    self._latest[key] = json.loads(payload)
            except zmq.Again:
                break

    def get_tof(self):
        """
        Return latest ToF readings: {"north": m, "south": m, "east": m, "west": m}
        or None if no data has arrived yet.
        """
        self._drain()
        return self._latest["tof"]

    def get_encoders(self):
        """
        Return latest encoder tick counts: {"north": ticks, ...}
        Ticks are cumulative since simulation start (signed, positive = forward).
        """
        self._drain()
        return self._latest["encoders"]

    def get_imu(self):
        """
        Return latest IMU reading: {"ax": m/s², "ay": m/s², "omega": rad/s}
        ax/ay are in robot body frame; omega is angular velocity (+ = CCW).
        """
        self._drain()
        return self._latest["imu"]

    def get_all(self):
        """Return all latest sensor readings in one dict."""
        self._drain()
        return dict(self._latest)

    def close(self):
        self.socket.close()
        self.context.term()
