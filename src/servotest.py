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

comp1 = 0
comp2 = 0
old_value1 = 1500
old_value2 = 1500
value1 = 1500
value2 = 1500
while (x != "exit"):
    x = input("QWERYUIO or 12346789")
    if x == "Q":
        comp1 = 100
    if x == "W":
        comp1 = 200
    if x == "E":
        comp1 = 300
    if x == "R":
        comp1 = 400
    if x == "T":
        comp1 = 500
    if x == "Y":
        comp1 = -100
    if x == "U":
        comp1 = -200
    if x == "I":
        comp1 = -300
    if x == "O": 
        comp1 = -400
    if x == "P":
        comp1 = -500 
    if x == "1":
        comp2 = 100
    if x == "2":
        comp2 = 200
    if x == "3":
        comp2 = 300
    if x == "4":
        comp2 = 400
    if x == "5":
        comp2 = 500
    if x == "6":
        comp2 = -100
    if x == "7":
        comp2 = -200
    if x == "8":
        comp2 = -300
    if x == "9": 
        comp2 = -400
    if x == "10":
        comp2 = -500
    old_value1 = value1
    print(old_value1)
    print(comp1)
    value1 = old_value1 + comp1
    print(value1)
    old_value2 = value2
    value2 += comp2
    if old_value1 < value1:
        for i in range(value1 - old_value1 + 1):
                pwm.set_servo_pulsewidth(servo1,old_value1 + i)
    elif old_value1 > value1:
        for i in range(old_value1 - value1 + 1):
                pwm.set_servo_pulsewidth(servo1,old_value1 - i)
    elif old_value1 == value1:
        pwm.set_servo_pulsewidth(servo1,old_value1)
    elif old_value2 < value2:
        for i in range(value2 - old_value2 + 1):
                pwm.set_servo_pulsewidth(servo2,old_value2 + i)
    elif old_value2 > value2:
        for i in range(old_value2 - value2 + 1):
                pwm.set_servo_pulsewidth(servo2,old_value2 - i)
    else:
        pwm.set_servo_pulsewidth(servo2,old_value2)
    time.sleep(1)

time.sleep(1)
pwm.set_servo_pulsewidth(servo1,1500)
time.sleep(1)
pwm.set_servo_pulsewidth(servo2,1500)


