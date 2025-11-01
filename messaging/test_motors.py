from Motor import PhaseEnableMotor
from time import sleep

motor = PhaseEnableMotor(pin1=17, pin2=27)


print(motor.forward(speed=1))
sleep(5)
print(motor.backward(speed=1))
sleep(5)
print(motor.stop())