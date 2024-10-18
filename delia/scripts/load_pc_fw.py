import sys
import i2c
import crc
import os
import re
import bl_regmap as bl
from intelhex import parse_hex, get_start_address, get_data_size
from time import sleep

# Constants
DEFAULT_SLAVE_ADDR = 8
PANEL_ADDRESS = 100
SCL_LOOPOUT = 1

# Globals
pcb = 'PCB_A'

def find_pc_mcu():
    # NOTE: Assumes the Panel MCU is in the bootloader state
    # Try accessing the panel address first - if this doesn't work
    # is PCB_B and we need to set the address
    msg = bl.encode('CHECK_FIRMWARE')
    status = i2c.write(PANEL_ADDRESS, msg)
    if status != i2c.OK:
        msg = bl.encode('CONFIG_I2C', [PANEL_ADDRESS, SCL_LOOPOUT])
        status = i2c.write(DEFAULT_SLAVE_ADDR, msg)
        global pcb
        pcb = 'PCB_B'
    return status == i2c.OK

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
    print('Firmware CRC:', hex(fw_crc))
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

def get_tag(slave_address):
    msg = bl.encode('CHECK_FIRMWARE')
    status = i2c.write(slave_address, msg)
    if status == i2c.OK:
        status, data = i2c.read(slave_address, 16)
        firmware_header = bl.decode('CHECK_FIRMWARE', data)
        return firmware_header[5][2]
    else:
        return 'ffffffff'

path = '/home/root/delia/firmware/'
file_list = os.listdir(path)
file_name_match = 'delia-panel-b\..\..-........\.hex'
pc_fw = ''

# Create a temporary file to show that this script has run
open('/tmp/load_pc_fw_run.txt', 'w')

# Open the i2c port
i2c.open()

# Find the panel controller MCU and program it
if find_pc_mcu() == True:
    print('PCB Revision: ' + 'A' if pcb == 'PCB_A' else 'B')
    print('Panel Controller MCU found')

    # Update filename if PCBA is detected
    if pcb == 'PCB_A':
        file_name_match = 'delia-panel-a\..\..-........\.hex'

    # Search the file name list for a matching firmware.
    for file_name in file_list:
        x = re.search(file_name_match, file_name)
        if x != None:
            pc_fw = os.path.join(path, x.string)

    if pc_fw == '':
        print('No firmware file found')
        sys.exit(1)
    else:
        print('Firmware file name: ', pc_fw);

    # Parse the firmware file
    records = parse_hex(pc_fw)
    PC_FW_TAG = pc_fw.split("-")[3].split(".")[0]
    PC_FW_SIZE, PC_FW_CRC = calculate_fw_crc(pc_fw)

    # Check the tag of programmed firmware - exit if already programmed
    firmware_tag = get_tag(PANEL_ADDRESS)
    if firmware_tag == PC_FW_TAG:
        # For rev B PCBs check the programmed CRC so we can reprogram in the case
        # of a corrupted flash
        if pcb == 'PCB_B':
            fw_crc = get_crc(PANEL_ADDRESS, PC_FW_SIZE)
            if fw_crc == PC_FW_CRC:
                print('Already programmed: CRC and TAG check succeeded')
                sys.exit(0)
            else:
                print('Firmware CRC mismatch - progam MCU: ' + hex(fw_crc) + ' (' + hex(PC_FW_CRC) + ')')
        else:
            print('Already programmed: TAG check succeeded')
            sys.exit(0)
    else:
        print('Firmware tag mismatch - progam MCU: ' + str(firmware_tag) + ' (' + str(PC_FW_TAG) + ')')

    print('Loading Panel Controller firmware: ' + pc_fw)
    firmware = load_firmware(PANEL_ADDRESS, pc_fw)

    # Ony check the CRC for PBC_B
    firmware_tag = get_tag(PANEL_ADDRESS)
    if firmware_tag != PC_FW_TAG:
        print('Error - MCU Firmware Tag Fail: ' + str(firmware_tag) + ' (' + str(PC_FW_TAG) + ')')
        sys.exit(1)

    if pcb == 'PCB_B':
        fw_crc = get_crc(PANEL_ADDRESS, PC_FW_SIZE)
        if fw_crc == PC_FW_CRC:
            print('MCU: Firmware OK')
        else:
            print('Error - MCU Firmware CRC Fail: ' + hex(fw_crc) + ' (' + hex(PC_FW_CRC) + ')')
            sys.exit(1)
    else:
        # No checks other than tag check for rev A
        print('MCU: Firmware OK')

    sys.exit(0)
else:
    print('PCB Revision: ' + 'A' if pcb == 'PCB_A' else 'B')
    print('Error - Panel Controller MCU was not found')
    sys.exit(1)
