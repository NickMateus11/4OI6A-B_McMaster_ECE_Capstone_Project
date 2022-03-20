from gpiozero import Servo
import pigpio
import time

x = "start"

servo1 = 25
servo2 = 24

pwm = pigpio.pi()
pwm.set_mode(servo1,pigpio.OUTPUT)
pwm.set_PWM_frequency(servo1,50)
pwm.set_mode(servo2,pigpio.OUTPUT)
pwm.set_PWM_frequency(servo2,50)


# range of pwm is 500-2500 -> 1500 is center (90 deg), while 1000/2000 are about 45/135 (or vice-versa)

pwm.set_servo_pulsewidth(servo1,1500)
pwm.set_servo_pulsewidth(servo2,1500)

while (x != "exit"):
    x = input("WASD5123?")
    if x == "W":
        print("0 deg")
        pwm.set_servo_pulsewidth(servo1,2000)
        time.sleep(3)
    if x == "S":
        print("90 deg")
        pwm.set_servo_pulsewidth(servo1,500)
        time.sleep(3)
    if x == "A":
        print("90 deg")
        pwm.set_servo_pulsewidth(servo1,1000)
        time.sleep(3)
    if x == "D":
        print("90 deg")
        pwm.set_servo_pulsewidth(servo1,1500)
        time.sleep(3)
    if x == "5":
        print("180 deg")
        pwm.set_servo_pulsewidth(servo2,2000)
        time.sleep(3)
    if x == "1":
        print("0 deg")
        pwm.set_servo_pulsewidth(servo2,500)
        time.sleep(3)
    if x == "2":
        print("60 deg")
        pwm.set_servo_pulsewidth(servo2,1000)
        time.sleep(3)
    if x == "3":
        print("120 deg")
        pwm.set_servo_pulsewidth(servo2,1500)
        time.sleep(3)



