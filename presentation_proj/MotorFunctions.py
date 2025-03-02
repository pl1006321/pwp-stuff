from adafruit_motorkit import MotorKit
import time
kit = MotorKit(0x40)

def forward():
    kit.motor1.throttle = -0.780
    # motor 1 is slightly weaker than motor 2 so adjustments had to be made
    kit.motor2.throttle = -0.775


def backward():
    kit.motor1.throttle = 0.780
    kit.motor2.throttle = 0.775
    # same throttles as moving forward, but negated values 


def left():
    # moves it backward slightly before turning 
    kit.motor1.throttle = -0.775 # moves right motor forward
    kit.motor2.throttle = 0.775 # moves left motor backward  
    # creates a councterclockwise spin
    # time.sleep(0.15) # allows for turning in small increments


def right():
    kit.motor1.throttle = 0.775 # moves right motor backward
    kit.motor2.throttle = -0.775 # moves left motor forward 
    # creates a clockwise spin
    # time.sleep(0.15) # allows for turning in small incremenets


def stop():
    kit.motor1.throttle = 0.0 # sets both motors speed to 0, stopping movement 
    kit.motor2.throttle = 0.0 
