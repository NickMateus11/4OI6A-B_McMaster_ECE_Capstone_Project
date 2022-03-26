import pigpio
import time
import random

'''

Start PI GPIO Daemon using:

sudo pigpiod

'''

servo1 = 4

pwm = pigpio.pi()
pwm.set_mode(servo1, pigpio.OUTPUT)
pwm.set_PWM_frequency(servo1, 50)


def smooth_rotate(gpio, target, current, step_size=20, delay=0.01):
    starting_val = current
    
    if (target < current):
        step_size = -abs(step_size)
    else:
        step_size = +abs(step_size)

    flag = False
    for i in range(abs((target-starting_val) // step_size)):
        val = (i+1)*step_size + starting_val
        if (val > 2500):
            val = 2500
            flag = True
        elif (val < 500):
            val = 500
            flag = True

        pwm.set_servo_pulsewidth(gpio, val)
        time.sleep(delay)

        if flag:
            break
    
    # check if stepping was exact - or if value needs to be updated one last time
    if (not ((target-starting_val) / step_size).is_integer()):
        pwm.set_servo_pulsewidth(gpio, target)


MID = 1500

def main():
    val=MID
    pwm.set_servo_pulsewidth(servo1, val) # 500-2500
    while (True):
        # x = input("+/-: ")
        # if x =='+':
        #     compensation = 100 
        # elif x=='-':
        #     compensation = -100
        # else:
        #     continue
        compensation = random.randint(50, 1000) * [-1,1][random.randrange(2)] # (50->100) * (-1 or 1) ==> (-1000->50) or (50->1000)

        old_val = val
        val += compensation
        if (val > 2500):
            val = 2500
        elif (val < 500):
            val = 500

        smooth_rotate(servo1, target=val, current=old_val)

pwm.set_servo_pulsewidth(servo1, 1500)


if __name__ == '__main__':
    main()
