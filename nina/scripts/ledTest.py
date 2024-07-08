import i2c
import time
import sys
from soakTestInterface import interface

# Constants
PANEL_ADDRESS = 100  
MAX_MOTOR_CONTROLLERS = 32
MC_DEFAULT_SLAVE_ADDR = 8
MC_BASE_SLAVE_ADDR = 50
SCL_LOOPOUT = 1

              
#if 'slow' is passed, then we run the soak test in slow mode                
n = len(sys.argv)
print("start")
print("Total arguments passed:", n)            
slow = False
if(n > 1):
    val = sys.argv[1]
    print(val)
    if(val == 'slow'):
        slow = True


soak_tester = interface()
soak_tester.startup()
counter = 0
led_on = False

while(1):
    counter +=1
    if(counter > 5000):
        counter = 0
        led_on = not(led_on)
    soak_tester.set_leds(led_on)
    