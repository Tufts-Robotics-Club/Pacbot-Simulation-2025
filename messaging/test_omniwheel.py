"""
Test script for 4-wheel omniwheel robot.
Tests motion patterns: forward, strafe, rotate, diagonal.

Corrected kinematics:
- Forward: W forward, E backward  (vy = (w-e)/2)
- Strafe right: N forward, S backward  (vx = (n-s)/2)
- Rotate CW: All forward  (omega = -(n+s+e+w)/4)

Make sure the simulator is running before executing this script!
Watch the simulator window to see the robot move.
"""

from Motor import PhaseEnableMotor
from time import sleep
import sys

# Pin configuration - must match simulator's MOTOR_PIN_CONFIG
NORTH_PINS = (17, 27)
SOUTH_PINS = (22, 23)
EAST_PINS = (24, 25)
WEST_PINS = (5, 6)


def main():
    print("=" * 60)
    print("Omniwheel Robot Motion Test (Corrected Kinematics)")
    print("=" * 60)
    print("\nMake sure the simulator is running!")
    print("Watch the simulator window to see the robot move.")
    print("Press Ctrl+C to stop.\n")

    try:
        # Create 4 motor instances
        print("Connecting motors...")
        motor_north = PhaseEnableMotor(pin1=NORTH_PINS[0], pin2=NORTH_PINS[1])
        motor_south = PhaseEnableMotor(pin1=SOUTH_PINS[0], pin2=SOUTH_PINS[1])
        motor_east = PhaseEnableMotor(pin1=EAST_PINS[0], pin2=EAST_PINS[1])
        motor_west = PhaseEnableMotor(pin1=WEST_PINS[0], pin2=WEST_PINS[1])
        print("Connected!\n")

        motors = {
            "north": motor_north,
            "south": motor_south,
            "east": motor_east,
            "west": motor_west,
        }

        def stop_all():
            for motor in motors.values():
                motor.stop()

        def print_test(name, description=""):
            print("\n" + "=" * 60)
            print(f"TEST: {name}")
            if description:
                print(f"  {description}")
            print("=" * 60)

        # Ensure starting from stopped state
        stop_all()
        sleep(0.5)

        # Test 1: Forward motion
        # vy = (w - e) / 2, so W forward + E backward = forward
        print_test("FORWARD", "W forward + E backward → robot moves up")
        motor_west.forward(0.6)
        motor_east.backward(0.6)
        sleep(2)
        stop_all()
        sleep(1)

        # Test 2: Backward motion
        print_test("BACKWARD", "W backward + E forward → robot moves down")
        motor_west.backward(0.6)
        motor_east.forward(0.6)
        sleep(2)
        stop_all()
        sleep(1)

        # Test 3: Strafe right
        # vx = (n - s) / 2, so N forward + S backward = strafe right
        print_test("STRAFE RIGHT", "N forward + S backward → robot moves right")
        motor_north.forward(0.6)
        motor_south.backward(0.6)
        sleep(2)
        stop_all()
        sleep(1)

        # Test 4: Strafe left
        print_test("STRAFE LEFT", "N backward + S forward → robot moves left")
        motor_north.backward(0.6)
        motor_south.forward(0.6)
        sleep(2)
        stop_all()
        sleep(1)

        # Test 5: Rotate clockwise (in place)
        # omega = -(n+s+e+w)/4, all forward = negative omega = CW
        print_test("ROTATE CW (in place)", "All wheels forward → pure rotation, NO translation")
        motor_north.forward(0.4)
        motor_south.forward(0.4)
        motor_east.forward(0.4)
        motor_west.forward(0.4)
        sleep(2)
        stop_all()
        sleep(1)

        # Test 6: Rotate counter-clockwise (in place)
        print_test("ROTATE CCW (in place)", "All wheels backward → pure rotation, NO translation")
        motor_north.backward(0.4)
        motor_south.backward(0.4)
        motor_east.backward(0.4)
        motor_west.backward(0.4)
        sleep(2)
        stop_all()
        sleep(1)

        # Test 7: Diagonal forward-right
        # Combine forward (W+, E-) with strafe right (N+, S-)
        print_test("DIAGONAL (Forward-Right)", "Combine forward + strafe")
        motor_west.forward(0.5)
        motor_east.backward(0.5)
        motor_north.forward(0.5)
        motor_south.backward(0.5)
        sleep(2)
        stop_all()
        sleep(1)

        # Test 8: Diagonal backward-left
        print_test("DIAGONAL (Backward-Left)", "Combine backward + strafe left")
        motor_west.backward(0.5)
        motor_east.forward(0.5)
        motor_north.backward(0.5)
        motor_south.forward(0.5)
        sleep(2)
        stop_all()
        sleep(1)

        # Test 9: Forward while rotating (arc)
        # Forward: W+, E-
        # Rotate: add same direction to all
        print_test("ARC MOTION", "Forward + rotation → curved path")
        motor_west.forward(0.7)   # Forward component
        motor_east.backward(0.3) # Reduced backward = some rotation
        motor_north.forward(0.2) # Rotation component
        motor_south.forward(0.2)
        sleep(3)
        stop_all()
        sleep(1)

        # Test 10: Square pattern
        print_test("SQUARE PATTERN", "Move in a square: up, right, down, left")
        moves = [
            ("Up", {"west": 0.5, "east": -0.5}),
            ("Right", {"north": 0.5, "south": -0.5}),
            ("Down", {"west": -0.5, "east": 0.5}),
            ("Left", {"north": -0.5, "south": 0.5}),
        ]
        for name, speeds in moves:
            print(f"  Moving {name}...")
            stop_all()
            sleep(0.2)
            for wheel, speed in speeds.items():
                if speed > 0:
                    motors[wheel].forward(abs(speed))
                else:
                    motors[wheel].backward(abs(speed))
            sleep(1.5)
        stop_all()
        sleep(1)

        print("\n" + "=" * 60)
        print("ALL MOTION TESTS COMPLETED!")
        print("=" * 60)
        print("\nCorrected kinematics summary:")
        print("  Forward:  W forward + E backward")
        print("  Strafe R: N forward + S backward")
        print("  Rotate:   All same direction (no translation!)")

    except KeyboardInterrupt:
        print("\n\nTest interrupted.")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        print("\nMake sure the simulator is running!")
        return 1
    finally:
        try:
            stop_all()
            for motor in motors.values():
                motor.close()
            print("\nMotors closed.")
        except:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
