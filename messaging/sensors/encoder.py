from .base import SensorBase, ID_TO_WHEEL


class Encoder(SensorBase):
    """
    Wheel encoder that reports cumulative tick count.

    sensor_id: 0=north, 1=south, 2=east, 3=west
    """

    def __init__(self, sensor_id, host="localhost", port=5557):
        super().__init__("sensors.encoders", host, port)
        if sensor_id not in ID_TO_WHEEL:
            raise ValueError(f"Invalid encoder id {sensor_id}; expected 0-3")
        self.sensor_id = sensor_id
        self._wheel = ID_TO_WHEEL[sensor_id]

    def read(self):
        """Return cumulative tick count (signed), or None if no data yet."""
        self._drain()
        if self._latest is None:
            return None
        return self._latest[self._wheel]
