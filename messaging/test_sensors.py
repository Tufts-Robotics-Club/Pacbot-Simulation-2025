"""Test script for all sensor types. Run alongside the simulator."""

import time
import math
from Sensor import SensorSubscriber

sensor = SensorSubscriber()
print("Listening for sensor data on port 5556...")
print("(Start the simulator if not already running)\n")

try:
    while True:
        all_data = sensor.get_all()

        tof = all_data["tof"]
        enc = all_data["encoders"]
        imu = all_data["imu"]

        if tof:
            print(f"ToF(m):  N={tof['north']:.3f}  S={tof['south']:.3f}  "
                  f"E={tof['east']:.3f}  W={tof['west']:.3f}")
        if enc:
            print(f"Enc(tk): N={enc['north']:8.1f}  S={enc['south']:8.1f}  "
                  f"E={enc['east']:8.1f}  W={enc['west']:8.1f}")
        if imu:
            print(f"IMU:     ax={imu['ax']:7.3f} m/s²  ay={imu['ay']:7.3f} m/s²  "
                  f"ω={math.degrees(imu['omega']):7.2f} °/s")
        if any(all_data.values()):
            print()

        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    sensor.close()
