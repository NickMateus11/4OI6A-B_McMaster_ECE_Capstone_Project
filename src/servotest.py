import pigpio
import time
import random

'''

Start PI GPIO Daemon using:

sudo pigpiod

'''

MAX_SERVO = 2500
MIN_SERVO = 500

ROT_RESTRICT_FACTOR = .10 # restict PWM to this much of full rotation
BIAS = 0

MAX_ADJUSTED = int(MAX_SERVO - (MAX_SERVO-MIN_SERVO)//2 * (1-ROT_RESTRICT_FACTOR)) + BIAS
MIN_ADJUSTED = int(MIN_SERVO + (MAX_SERVO-MIN_SERVO)//2 * (1-ROT_RESTRICT_FACTOR)) + BIAS


SERVO_PIN_1 = 4

pwm = pigpio.pi()
pwm.set_mode(SERVO_PIN_1, pigpio.OUTPUT)
pwm.set_PWM_frequency(SERVO_PIN_1, 50)


def smooth_rotate(gpio, target, step_size=20, delay=0.1):
    starting_val = pwm.get_servo_pulsewidth(gpio) - BIAS
    
    if (target < starting_val):
        step_size = -abs(step_size)
    else:
        step_size = +abs(step_size)

    flag = False
    for i in range(abs((target-starting_val) // step_size)):
        val = (i+1)*step_size + starting_val
        print(val)
        if (val > MAX_ADJUSTED):
            val = MAX_ADJUSTED
            flag = True
        elif (val < MIN_ADJUSTED):
            val = MIN_ADJUSTED
            flag = True

        pwm.set_servo_pulsewidth(gpio, val+BIAS )
        time.sleep(delay)

        if flag:
            break
    
    # check if stepping was exact - or if value needs to be updated one last time
    if (not ((target-starting_val) / step_size).is_integer()):
        print(val)
        pwm.set_servo_pulsewidth(gpio, target)



def main():
    try:
        val=(MAX_ADJUSTED+MIN_ADJUSTED)//2
        pwm.set_servo_pulsewidth(SERVO_PIN_1, val+BIAS) # 500-2500
        while (True):
            x = input("+/-: ")
            if x =='+':
                compensation = 100 
            elif x=='-':
                compensation = -100
            else:
                continue
            # compensation = random.randint(50, 1000) * [-1,1][random.randrange(2)] # (50->100) * (-1 or 1) ==> (-1000->50) or (50->1000)

            val += compensation
            if (val > MAX_ADJUSTED):
                val = MAX_ADJUSTED
            elif (val < MIN_ADJUSTED):
                val = MIN_ADJUSTED

            smooth_rotate(SERVO_PIN_1, target=val)
            time.sleep(0.5)

    except KeyboardInterrupt:
        pass
    
    pwm.set_servo_pulsewidth(SERVO_PIN_1, (MAX_ADJUSTED+MIN_ADJUSTED)//2+BIAS)


if __name__ == '__main__':
    main()
