import pigpio
import time
import random

'''

Start PI GPIO Daemon using:

sudo pigpiod

'''

MAX_SERVO = 2500
MIN_SERVO = 500

ROT_RESTRICT_FACTOR = 0.22 # restict PWM to this much of full rotation

MAX_ADJUSTED = int(MAX_SERVO - (MAX_SERVO-MIN_SERVO)//2 * (1-ROT_RESTRICT_FACTOR))
MIN_ADJUSTED = int(MIN_SERVO + (MAX_SERVO-MIN_SERVO)//2 * (1-ROT_RESTRICT_FACTOR))


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
        if (val > MAX_ADJUSTED):
            val = MAX_ADJUSTED
            flag = True
        elif (val < MIN_ADJUSTED):
            val = MIN_ADJUSTED
            flag = True

        pwm.set_servo_pulsewidth(gpio, val)
        time.sleep(delay)

        if flag:
            break
    
    # check if stepping was exact - or if value needs to be updated one last time
    if (not ((target-starting_val) / step_size).is_integer()):
        pwm.set_servo_pulsewidth(gpio, target)



def main():
    val=(MAX_ADJUSTED+MIN_ADJUSTED)//2
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
        if (val > MAX_ADJUSTED):
            val = MAX_ADJUSTED
        elif (val < MIN_ADJUSTED):
            val = MIN_ADJUSTED

        smooth_rotate(servo1, target=val, current=old_val)

pwm.set_servo_pulsewidth(servo1, (MAX_ADJUSTED+MIN_ADJUSTED)//2)


if __name__ == '__main__':
    main()
