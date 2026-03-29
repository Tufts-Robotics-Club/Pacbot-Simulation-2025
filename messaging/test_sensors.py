"""Test script for ToF sensor subscriber. Run alongside the simulator."""

import time
from Sensor import SensorSubscriber

sensor = SensorSubscriber()
print("Listening for ToF sensor data on port 5556...")
print("(Start the simulator if not already running)\n")

try:
    while True:
        tof = sensor.get_tof()
        if tof is not None:
            print(f"ToF:  N={tof['north']:.3f}m  S={tof['south']:.3f}m  "
                  f"E={tof['east']:.3f}m  W={tof['west']:.3f}m")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    sensor.close()
