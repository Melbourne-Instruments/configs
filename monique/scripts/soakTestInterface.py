import i2c
import time
import sys

# Constants
PANEL_ADDRESS = 100  
MAX_MOTOR_CONTROLLERS = 21
MC_DEFAULT_SLAVE_ADDR = 8
MC_BASE_SLAVE_ADDR = 50
SCL_LOOPOUT = 1

class interface():
    mc_slaves = []
    def startup(self):
        i2c.open()
        for i in range(MAX_MOTOR_CONTROLLERS):
            self.mc_slaves.append(MC_BASE_SLAVE_ADDR + i)
        print(self.mc_slaves)
        
    def go_to_pos_1(self, pos):
        for slave in self.mc_slaves:
                i2c.write(slave, '296070')
    def go_to_pos_2(self, pos):
        for slave in self.mc_slaves:
                i2c.write(slave, '29a00f')
                
    def set_leds(self,enable):
        led_status = 0
        if enable == True:
            for led in range(45):
                led_status |= (1 << led)
        msg = '01{0:08x}'.format(led_status)   
        i2c.write(100, msg)
