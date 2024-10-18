import sys
import i2c
import crc
import bl_regmap as bl
import mc_regmap as mc
from intelhex import parse_hex, get_start_address, get_data_size
from time import sleep

# Constants
DEFAULT_SLAVE_ADDR = 8
PANEL_ADDRESS = 100
MOTOR_BASE_ADDRESS = 50
NUM_MOTORS = 21
SCL_LOOPOUT = 1
Position_Kp = 5120
Position_Ki = 208
Position_Kd = 480

# Globals
pcb = 'PCB_A'

def find_mc_mcus():
    # NOTE: Assumes the MCUs are in the bootloader state
    # Try accessing the panel address first - if this doesn't work
    # is PCB_B and we need to set the address of the panel controller
    msg = bl.encode('CHECK_FIRMWARE')
    status = i2c.write(PANEL_ADDRESS, msg)
    if status != i2c.OK:
        msg = bl.encode('CONFIG_I2C', [PANEL_ADDRESS, SCL_LOOPOUT])
        status = i2c.write(DEFAULT_SLAVE_ADDR, msg)
        global pcb
        pcb = 'PCB_B'

    # Loop through and set the address of each motor
    num_mcus = 0
    slave_address = MOTOR_BASE_ADDRESS
    msg = bl.encode('CHECK_FIRMWARE')
    status = i2c.write(DEFAULT_SLAVE_ADDR, msg)
    while num_mcus < NUM_MOTORS and status == i2c.OK:
        msg = bl.encode('CONFIG_I2C', [slave_address, SCL_LOOPOUT])
        status = i2c.write(DEFAULT_SLAVE_ADDR, msg)
        slave_address += 1
        num_mcus += 1
        msg = bl.encode('CHECK_FIRMWARE')
        status = i2c.write(DEFAULT_SLAVE_ADDR, msg)
    return num_mcus

def load_firmware(slave_address, fw_filename):
    records = parse_hex(fw_filename)
    # Get required info from firmware records 
    start_address = get_start_address(records)
    data_size = get_data_size(records)
    FLASH_BASE = 0x08000000
    flash_offset = int(start_address, 16) - FLASH_BASE
    start_page = (flash_offset) >> 11
    num_pages = data_size >> 11
    if data_size & 0x7ff:
        num_pages += 1
    print('Programming Slave {}'.format(slave_address))
    print('Preparing {} pages of flash for programming starting at page {}'.format(num_pages, start_page))
    msg = bl.encode('START_PROGRAMMING', [data_size, flash_offset])
    status = i2c.write(slave_address, msg)
        
    device_status = ''
    while device_status != 'READY_FOR_DATA':  # Should check for INVALID_ADDRESS, PARAM_SIZE_ERROR 
        sleep(0.1)
        status, reg_value = i2c.read(slave_address, 1)
        device_status = bl.status_t[int(reg_value, 16)]
        # Should see a few 'BUSY' responses before 'READY FOR DATA' pops up once FLASH_ERASE complete
        print(device_status,)

    index = 1
    num_records = data_size//16
    while index <= num_records:
        addr = int(records[index]['address'], 16) + FLASH_BASE
        data = int(records[index]['data'], 16)
        # checksum = records[index]['checksum']  # Have not implemented Checksum in bootloader yet
        msg = bl.encode('WRITE_FIRMWARE', [data, addr])
        status = i2c.write(slave_address, msg)
        print('  {0}/{1} {2:.2f}%'.format(index*16, data_size, index*16/data_size*100), end="\r")
        
        if index == (num_records):
            break
    
        device_status = ''
        while device_status != 'READY_FOR_DATA':  # Should check for other return type errors
            status, reg_value = i2c.read(slave_address, 1)
            try:
                device_status = bl.status_t[int(reg_value, 16)]
            except:
                print(reg_value)
            # print(device_status)
        index += 1
    
    sleep(0.01)
    status, reg_value = i2c.read(slave_address, 1)
    device_status = bl.status_t[int(reg_value, 16)]
    print('  {}'.format(device_status))
    # Check firmware version and update MCU's
    firmware = 'None'
    msg = bl.encode('CHECK_FIRMWARE')
    status = i2c.write(slave_address, msg)
    if status == i2c.OK:
        status, data = i2c.read(slave_address, 16)
        firmware = bl.decode('CHECK_FIRMWARE', data)
    return firmware

def calculate_fw_crc(fw_filename):
    records = parse_hex(fw_filename)
    data_size = get_data_size(records)

    index = 1
    num_records = data_size//16
    crc_data = bytearray()

    while index <= num_records:
        int_record = int(records[index]['data'], 16)
        crc_data += int_record.to_bytes(16, 'big')
        index += 1

    fw_crc = crc.crc32_stm(crc_data)
    print(f'Firmware CRC: ', hex(fw_crc))
    return(data_size, fw_crc)

def get_crc(slave_address, data_size):
    mcu_crc = 0
    # Calculate CRC
    msg = '07' + data_size.to_bytes(4, 'big').hex() 
    status = i2c.write(slave_address, msg)
    if status == i2c.OK:
        #sleep(0.01)
        status, data = i2c.read(slave_address, 1)
        while data != '00': # Wait until CRC calculated (returns IDLE)
            status, data = i2c.read(slave_address, 1)

    # Read CRC
    msg = '06' 
    status = i2c.write(slave_address, msg)
    if status == i2c.OK:
        status, data = i2c.read(slave_address, 4)
        # Swap32
        mcu_crc = int.from_bytes(int(data ,16).to_bytes(4, byteorder='little'), byteorder='big', signed=False)

    print('Slave', slave_address, 'crc', hex(mcu_crc))
    return mcu_crc 

def write_reg(addr, register, params=[]):
    msg = mc.encode(register, params)
    status = i2c.write(addr, msg)
    sleep(0.001)
    if status < 0:
        raise Exception("Write register {} FAILED, {}".format(register, status))
        sys.exit(1)
    #else:
    #    print('write_reg({}, {}, {})'.format(addr, register, params))

def set_pos_pid_values(addr, Kp, Ki, Kd):
        # Write the default values
        write_reg(addr, 'MOTION_POSITION_KP', [Kp])
        write_reg(addr, 'MOTION_POSITION_KI', [Ki])
        write_reg(addr, 'MOTION_POSITION_KD', [Kd])
        write_reg(addr, 'FLASH_CONFIG_WRITE', [1])
        # Done, show time taken
        print("  Position PID values: {} {} {} saved to {}".format(Kp, Ki, Kd, addr))

def get_tag(slave_address):
    msg = bl.encode('CHECK_FIRMWARE')
    status = i2c.write(slave_address, msg)
    if status == i2c.OK:
        status, data = i2c.read(slave_address, 16)
        firmware_header = bl.decode('CHECK_FIRMWARE', data)
        return firmware_header[5][2]
    else:
        return 'ffffffff'

# Get the arguments passsed - should be just one, the Motor Controller
# firmware to update
n = len(sys.argv)
if (n == 1):
    print("The Motor Controller firmware must be passed to this script")
    sys.exit(1)
if (n != 2):
    print("The Motor Controller firmware must be the only argument passed to this script")
    sys.exit(1)
mc_fw = sys.argv[1]
print('Loading Motor Controller firmare: ' + mc_fw)

# Create a temporary file to show that this script has run
open('/tmp/load_mc_fw_run.txt', 'w')

# Open the i2c port
i2c.open()

# Parse the firmware file
records = parse_hex(mc_fw)
MC_FW_TAG = mc_fw.split("-")[3].split(".")[0]
MC_FW_SIZE, MC_FW_CRC = calculate_fw_crc(mc_fw)

# Find the Motor Controller MCUs
num_mcus = find_mc_mcus()
print('PCB Revision: ' + 'A' if pcb == 'PCB_A' else 'B')
print('Motor Controller MCUs found: ' + str(num_mcus) + ' (expected ' + str(NUM_MOTORS) + ')')

if num_mcus > 0:
    for x in range(num_mcus):
        addr = MOTOR_BASE_ADDRESS + x

        # Check the tag of programmed firmware - exit if already programmed
        firmware_tag = get_tag(addr)
        if firmware_tag == MC_FW_TAG:
            # For rev B PCBs check the programmed CRC so we can reprogram in the case
            # of a corrupted flash
            if pcb == 'PCB_B':
                fw_crc = get_crc(addr, MC_FW_SIZE)
                if fw_crc == MC_FW_CRC:
                    print('Already programmed: CRC and TAG check succeeded')
                    msg = bl.encode('START_FIRMWARE')
                    status = i2c.write(addr, msg)
                    continue
                else:
                    print('Firmware CRC mismatch - progam MCU: ' + hex(fw_crc) + ' (' + hex(MC_FW_CRC) + ')')
            else:
                print('Already programmed: TAG check succeeded')
                msg = bl.encode('START_FIRMWARE')
                status = i2c.write(addr, msg)
                continue
        else:
            print('Firmware tag mismatch - progam MCU: ' + str(firmware_tag) + ' (' + str(MC_FW_TAG) + ')')

        firmware = load_firmware(addr, mc_fw)

        # Ony check the CRC for PBC_B
        firmware_tag = get_tag(addr)
        if firmware_tag != MC_FW_TAG:
            print('Error - MCU ' + str(x + 1) + ': Firmware Tag Fail: ' + str(firmware_tag) + ' - ' + str(MC_FW_TAG))
            sys.exit(1)

        if pcb == 'PCB_B':
            fw_crc = get_crc(addr, MC_FW_SIZE)
            if fw_crc == MC_FW_CRC:
                print('MCU ' + str(x + 1) + ': Firmware OK')
            else:
                print('Error - MCU ' + str(x + 1) + ': Firmware CRC Fail')
                sys.exit(1)
        else:
            print('MCU ' + str(x + 1) + ': Firmware OK')

        # If we succeeded programming restart the MCU
        sleep(0.01)
        msg = bl.encode('START_FIRMWARE')
        status = i2c.write(addr, msg)
        sleep(0.1)
        set_pos_pid_values(addr, Position_Kp, Position_Ki, Position_Kd)

    sys.exit(0)
else:
    print('Error - No Motor Controller MCUs were found')
    sys.exit(1)
