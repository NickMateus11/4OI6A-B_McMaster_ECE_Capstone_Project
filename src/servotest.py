from platform import release
import pigpio
import time
import random

'''

Start PI GPIO Daemon using:

sudo pigpiod

'''

MAX_SERVO = 2500
MIN_SERVO = 500

ROT_RESTRICT_FACTOR = .07 # restict PWM to this much of full rotation

MAX_ADJUSTED = int(MAX_SERVO - (MAX_SERVO-MIN_SERVO)//2 * (1-ROT_RESTRICT_FACTOR))
MIN_ADJUSTED = int(MIN_SERVO + (MAX_SERVO-MIN_SERVO)//2 * (1-ROT_RESTRICT_FACTOR))


SERVO_PIN_1 = 4
SERVO_PIN_2 = 17
BIAS1 = 600
BIAS2 = -600

pwm = pigpio.pi()

pwm.set_mode(SERVO_PIN_1, pigpio.OUTPUT)
pwm.set_PWM_frequency(SERVO_PIN_1, 50)
pwm.set_mode(SERVO_PIN_2, pigpio.OUTPUT)
pwm.set_PWM_frequency(SERVO_PIN_2, 50)

def initilizePWM(gpio, pwm_val, bias):
    pwm.set_mode(gpio, pigpio.OUTPUT)
    pwm.set_PWM_frequency(gpio, 100)
    pwm.set_servo_pulsewidth(gpio, pwm_val+bias)

def releasePWM(gpio):
    pwm.set_servo_pulsewidth(gpio, 0)

def current_pwm(gpio, bias):
    return pwm.get_servo_pulsewidth(gpio) - bias

def smooth_rotate(gpio, target, step_size=5, delay=0.01, bias=0):
    starting_val = current_pwm(gpio, bias)
    
    if (target < starting_val):
        step_size = -abs(step_size)
    else:
        step_size = +abs(step_size)

    flag = False
    for i in range(abs((target-starting_val) // step_size)):
        val = (i+1)*step_size + starting_val
        # print(val)
        if (val > MAX_ADJUSTED):
            val = MAX_ADJUSTED
            flag = True
        elif (val < MIN_ADJUSTED):
            val = MIN_ADJUSTED
            flag = True

        pwm.set_servo_pulsewidth(gpio, val+bias)
        time.sleep(delay)

        if flag:
            break
    
    # check if stepping was exact - or if value needs to be updated one last time
    # if (current_pwm(gpio, bias) != target):
    #     print(target)
    #     pwm.set_servo_pulsewidth(gpio, target+bias)
    
    time.sleep(0.2)
    return current_pwm(gpio, bias)


def main():
    pwm1 = None
    pwm2 = None
    try:
        val=(MAX_ADJUSTED+MIN_ADJUSTED)//2
        pwm.set_servo_pulsewidth(SERVO_PIN_1, val+BIAS1)
        pwm1 = val+BIAS1
        while (True):
            x = input("+/-: ")
            if x =='+':
                compensation = 50 
            elif x=='-':
                compensation = -50
            else:
                continue

            val += compensation
            if (val > MAX_ADJUSTED):
                val = MAX_ADJUSTED
            elif (val < MIN_ADJUSTED):
                val = MIN_ADJUSTED

            pwm1 = smooth_rotate(SERVO_PIN_1, target=val, bias=BIAS1)
            print(pwm1)

            time.sleep(0.5)

    except KeyboardInterrupt:
        pass
    
    smooth_rotate(SERVO_PIN_1, target=(MAX_ADJUSTED+MIN_ADJUSTED)//2, bias=BIAS1)
    releasePWM(SERVO_PIN_1)


if __name__ == '__main__':
    initilizePWM(SERVO_PIN_1, (MAX_ADJUSTED+MIN_ADJUSTED)//2, bias=BIAS1)
    main()
