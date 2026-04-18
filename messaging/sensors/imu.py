from .base import SensorBase


class IMU(SensorBase):
    """
    Inertial Measurement Unit mounted at the robot center.
    Provides body-frame linear acceleration and angular velocity.
    (Singleton — there's only one IMU, so no id needed.)
    """

    def __init__(self, host="localhost", port=5557):
        super().__init__("sensors.imu", host, port)

    def read(self):
        """
        Return dict {"ax": m/s², "ay": m/s², "omega": rad/s} in body frame,
        or None if no data yet.
        """
        self._drain()
        return self._latest

    def read_accel(self):
        """Return (ax, ay) in body frame m/s², or None."""
        data = self.read()
        return (data["ax"], data["ay"]) if data else None

    def read_gyro(self):
        """Return omega (rad/s, + = CCW), or None."""
        data = self.read()
        return data["omega"] if data else None
