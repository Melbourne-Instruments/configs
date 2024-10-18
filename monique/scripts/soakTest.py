import i2c
import time
import sys
from soakTestInterface import interface

# Constants
PANEL_ADDRESS = 100  
MAX_MOTOR_CONTROLLERS = 21
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
while(1):
        
    if(slow):
        soak_tester.go_to_pos_1(4000)
        time.sleep(0.5)
        soak_tester.go_to_pos_2(32768 - 4000)
        time.sleep(0.2)
    else:
        soak_tester.go_to_pos_1(4000)
        time.sleep(0.2)
        soak_tester.go_to_pos_2(32768 - 4000)
        time.sleep(0.2)
    