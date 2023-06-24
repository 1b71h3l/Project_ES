import RPi.GPIO as GPIO
import time

# Set GPIO mode
GPIO.setmode(GPIO.BOARD)

# Set the GPIO pin number for the servo
servo_pin = 11

# Set the frequency for PWM
frequency = 50

# Set duty cycle limits for the servo
duty_cycle_min = 2
duty_cycle_max = 12

# Configure the GPIO pin for PWM
GPIO.setup(servo_pin, GPIO.OUT)
pwm = GPIO.PWM(servo_pin, frequency)

# Function to set the angle of the servo motor
def set_angle(angle):
    duty_cycle = ((angle / 180.0) * (duty_cycle_max - duty_cycle_min)) + duty_cycle_min
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.3)

# Test the servo motor by sweeping it back and forth
try:
    pwm.start(duty_cycle_min)
    while True:
        # Sweep from 0 to 180 degrees
        for angle in range(0, 181, 10):
            set_angle(angle)

        # Sweep from 180 to 0 degrees
        for angle in range(180, -1, -10):
            set_angle(angle)

except KeyboardInterrupt:
    # Stop PWM and clean up GPIO
    pwm.stop()
    GPIO.cleanup()


