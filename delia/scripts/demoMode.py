import i2c
import time
import random

# Constants
MAX_MOTOR_CONTROLLERS = 21
MC_BASE_SLAVE_ADDR = 50

def go_to_random_pos(mc_slaves):
    for slave in mc_slaves:
        # Set the knob to a random position between 0 and 32767
        # Note the knob data is little endian
        pos = random.randint(0,32767)
        pos_msb = pos >> 8
        pos_lsb = pos & 0xff
        i2c.write(slave, '29' + f"{pos_lsb:02x}" + f"{pos_msb:02x}")

# Set the MC addresses
mc_slaves = []
for i in range(MAX_MOTOR_CONTROLLERS):
    mc_slaves.append(MC_BASE_SLAVE_ADDR + i)

# Open the i2c port
i2c.open()

# Loop setting each motor to a random positions
while(1):
    go_to_random_pos(mc_slaves)
    time.sleep(1)
    