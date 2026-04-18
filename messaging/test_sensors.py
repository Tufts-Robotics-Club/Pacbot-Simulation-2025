"""Test script for all sensor types. Run alongside the simulator."""

import time
import math
from sensors import ToFSensor, Encoder, IMU

# Instantiate one of each per wheel, plus the IMU
tofs = {name: ToFSensor(i) for i, name in enumerate(["N", "S", "E", "W"])}
encs = {name: Encoder(i) for i, name in enumerate(["N", "S", "E", "W"])}
imu = IMU()

print("Listening for sensor data on port 5557...")
print("(Start the simulator if not already running)\n")

try:
    while True:
        tof_vals = {k: s.read() for k, s in tofs.items()}
        enc_vals = {k: s.read() for k, s in encs.items()}
        imu_data = imu.read()

        if all(v is not None for v in tof_vals.values()):
            print("ToF(m):  " + "  ".join(f"{k}={v:.3f}" for k, v in tof_vals.items()))
        if all(v is not None for v in enc_vals.values()):
            print("Enc(tk): " + "  ".join(f"{k}={v:8.1f}" for k, v in enc_vals.items()))
        if imu_data:
            print(f"IMU:     ax={imu_data['ax']:7.3f} m/s²  "
                  f"ay={imu_data['ay']:7.3f} m/s²  "
                  f"ω={math.degrees(imu_data['omega']):7.2f} °/s")
            print()

        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    for s in list(tofs.values()) + list(encs.values()):
        s.close()
    imu.close()
