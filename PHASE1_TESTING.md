# Phase 1 Testing Guide

## What Was Implemented

Phase 1 establishes the motor command interface between control code and simulator:

### Architecture
```
Control Code                    Simulator
┌──────────────────┐           ┌──────────────────┐
│ PhaseEnableMotor │ ──ZMQ──▶  │ Receives command │
│   (pin 17, 27)   │           │ Maps to NORTH    │
│ .forward(0.5)    │           │ Stores speed     │
└──────────────────┘           └──────────────────┘
       ×4 motors                  Tracks all 4
```

### Motor → Wheel Mapping
The simulator identifies which wheel each motor controls by pin numbers:
```python
MOTOR_PIN_CONFIG = {
    (17, 27): "north",   # Top wheel (horizontal)
    (22, 23): "south",   # Bottom wheel (horizontal)
    (24, 25): "east",    # Right wheel (vertical)
    (5, 6):   "west",    # Left wheel (vertical)
}
```

### PhaseEnableMotor Interface (Unchanged)
```python
motor = PhaseEnableMotor(pin1=17, pin2=27)
motor.forward(speed=0.8)   # Speed 0.0 to 1.0
motor.backward(speed=0.8)  # Speed 0.0 to 1.0
motor.stop()               # Stop the motor
motor.close()              # Clean up
```

---

## How to Test

### Step 1: Start the Simulator

```bash
cd simulator
python simulator.py
```

You should see:
- Terminal output showing pin configuration
- Pygame window with:
  - Robot diagram (circle with 4 wheels at N/S/E/W)
  - Motor speed bars for each wheel
  - Pin configuration reference

### Step 2: Run the Test Script

In a **second terminal**:

```bash
cd messaging
python test_omniwheel.py
```

This runs 10 tests:

1. **Stop All Motors** - Verify all wheels stop
2. **Individual Wheel Forward** - Each wheel forward separately
3. **Individual Wheel Backward** - Each wheel backward separately
4. **Forward Motion** - E+W wheels forward (robot would move forward)
5. **Strafe Left** - N forward + S backward
6. **Strafe Right** - N backward + S forward
7. **Rotate Clockwise** - All wheels forward
8. **Rotate Counter-Clockwise** - All wheels backward
9. **Diagonal Motion** - Combination
10. **Variable Speed** - Speed ramping test

### Step 3: Verify Behavior

Watch the simulator window as tests run:

| Test | Expected Wheel Colors |
|------|----------------------|
| North forward | N = green, others = gray |
| South backward | S = red, others = gray |
| Forward motion | E+W = green |
| Strafe left | N = green, S = red |
| Rotate CW | All = green |
| Rotate CCW | All = red |

---

## Manual Testing

### Quick Test Script
```python
from Motor import PhaseEnableMotor
from time import sleep

# Create 4 motors
n = PhaseEnableMotor(17, 27)  # North
s = PhaseEnableMotor(22, 23)  # South
e = PhaseEnableMotor(24, 25)  # East
w = PhaseEnableMotor(5, 6)    # West

# Test: Move forward (E+W)
e.forward(0.5)
w.forward(0.5)
sleep(2)

# Test: Strafe left (N forward, S backward)
n.forward(0.5)
s.backward(0.5)
e.stop()
w.stop()
sleep(2)

# Stop all
for motor in [n, s, e, w]:
    motor.stop()
    motor.close()
```

### Testing Different Pin Configurations

If your real robot uses different pins, update `MOTOR_PIN_CONFIG` in `simulator/simulator.py` and the pin constants in your test scripts.

---

## Expected Results

### Successful Test Output
```
============================================================
4-Wheel Omniwheel Motor Test
============================================================

Make sure the simulator is running first!

Creating motor instances...
All motors connected!

============================================================
TEST: Stop All Motors
============================================================
All motors stopped.

============================================================
TEST: Individual Wheel Forward
============================================================
  NORTH wheel forward...
    Response: {"status": "ok", "command": "forward", ...}
  SOUTH wheel forward...
  ...

============================================================
ALL TESTS COMPLETED!
============================================================
```

### Simulator Terminal Output
```
============================================================
Pacbot Simulator Started
============================================================
Listening on port 5555
Motor pin configuration:
  Pins (17, 27) -> north wheel
  Pins (22, 23) -> south wheel
  Pins (24, 25) -> east wheel
  Pins (5, 6) -> west wheel
============================================================
Received: {'command': 'forward', 'pin1': 17, 'pin2': 27, 'params': {'speed': 0.8}}
Response: {'status': 'ok', 'command': 'forward', 'pin1': 17, 'pin2': 27, 'wheel': 'north', 'message': 'north wheel forward at 0.8'}
...
```

---

## Troubleshooting

### "Unknown motor pins" Warning
**Cause**: Pin numbers in test script don't match simulator config

**Fix**: Either:
1. Update test script pins to match `MOTOR_PIN_CONFIG`
2. Update `MOTOR_PIN_CONFIG` in simulator to match your pins

### Connection Refused
**Cause**: Simulator not running

**Fix**: Start simulator first: `python simulator/simulator.py`

### Motors Don't Respond
**Cause**: ZeroMQ socket issue

**Fix**:
1. Close and restart simulator
2. Close and restart test script
3. Check port 5555 is not in use: `lsof -i :5555`

---

## Checklist

Phase 1 is complete when:

- [ ] Simulator starts and shows robot diagram
- [ ] All 4 motors connect successfully
- [ ] Individual wheel commands update correct wheel
- [ ] Wheel colors change: green=forward, red=backward, gray=stopped
- [ ] Speed bars reflect motor speed magnitude
- [ ] Unknown pins show warning (not crash)
- [ ] Press 'R' resets all motors to stopped

---

## What's Next (Phase 2)

Phase 1 only establishes communication. The robot diagram shows motor **states** but doesn't **move**.

Phase 2 will add:
- Robot physics (motor speeds → robot velocity)
- Actual robot movement in the maze
- Position/orientation tracking

The control code interface (`PhaseEnableMotor`) remains **unchanged** - all physics happens inside the simulator.
