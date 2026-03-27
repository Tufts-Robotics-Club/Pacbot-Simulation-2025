"""Test script for sensor subscriber. Run alongside the simulator."""

import time
import math
from Sensor import SensorSubscriber

sensor = SensorSubscriber()
print("Listening for sensor data on port 5556...")
print("(Start the simulator if not already running)\n")

try:
    while True:
        pos = sensor.get_position()
        if pos is not None:
            x, y, theta = pos
            print(f"Position: x={x:.4f}m  y={y:.4f}m  theta={math.degrees(theta):.1f}°")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    sensor.close()
