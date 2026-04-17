from Motor import Motor
from time import sleep

motor = Motor(0)  # North


print(motor.forward(speed=1))
sleep(5)
print(motor.backward(speed=1))
sleep(5)
print(motor.stop())
