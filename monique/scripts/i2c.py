import sys
import os
import fcntl
from time import sleep

# Constants
I2C_PORT  = "6"
I2C_SLAVE = 0x0703
ETIMEDOUT = 110
EREMOTEIO = 121
OK = 0
NACK = -1
TIMEOUT = -2
# Variables
handle = None


def open():
    global handle
    try:
        handle = os.open("/dev/i2c-" + I2C_PORT, os.O_RDWR)
    except:
        raise Exception("An error occurred opening I2C port " + I2C_PORT)


def close():
    global handle
    if handle is not None:
        os.close(handle)
        handle = None


def select_slave(slave_addr):
    try:
        # Set the slave address
        fcntl.ioctl(handle, I2C_SLAVE, slave_addr)
    except OSError as ex:
        print('Error setting slave address', ex)
        raise ex


def write(slave_addr, buf):
    global handle
    if handle is None:
        raise Exception("The I2C port is not open")
    if len(buf) < 2 or ((len(buf) % 2) != 0):
        raise Exception("Passed write buffer is not valid")

    # print('Attempting i2c_wr 0x{} to slave address {}'.format(buf, slave_addr))

    try:
        # Set the slave address
        fcntl.ioctl(handle, I2C_SLAVE, slave_addr)
    except OSError as ex:
        print('Error setting slave address')
        raise ex

    retry = 5

    while True:
        try:
            # Write the data
            if sys.version_info.major == 3: 
                ret = os.write(handle, bytes.fromhex(buf))
            else:
                ret = os.write(handle, bytearray.fromhex(buf))
            # print('i2c_wr', slave_addr, buf, len(buf)//2, ret)
            # sleep(0.01)
            if ret == (len(buf)//2): 
                # If all bytes in buffer written is as expected return OK (0)
                return OK
            else:
                # Else return number of bytes succesfully written
                if retry:
                    retry = retry - 1
                    #sleep(0.001)
                print(ret)
                return ret
        
        except OSError as ex:
            # Was a NACK was received?
            if ex.args[0] == EREMOTEIO:
                if retry:
                    # print('NACK retry write', slave_addr, buf)
                    retry = retry - 1
                    #sleep(0.001)
                else:
                    print('I2C NACKED 5 times writing to slave', slave_addr)
                    return NACK

            elif ex.args[0] == ETIMEDOUT:
                return TIMEOUT
            else:
                print('I2C Write Error', ex.args[0], slave_addr)
                # raise ex
    
        except Exception as ex:
            raise ex("An error occurred writing to the I2C device")

    
def read(slave_addr, read_len):
    global handle
    if handle is None:
        raise Exception("The I2C port is not open")
    if read_len == 0:
        raise Exception("The I2C read length is invalid")

    try:
        # Set the slave address
        fcntl.ioctl(handle, I2C_SLAVE, slave_addr)
    except OSError as ex:
        print('Error setting slave address')
        raise ex

    retry = 5
    while True:
        try:
            # Read the data
            buf = os.read(handle, read_len)
    
            if sys.version_info.major == 3:  
                return OK, buf.hex()
            else:
                return OK, buf.encode('hex')
        
        except OSError as ex:
            # Was a NACK was received?
            if ex.args[0] == EREMOTEIO:
                if retry:
                    # print('NACK retry read', slave_addr, read_len)
                    retry = retry - 1
                    #sleep(0.001)
                else:
                    print('I2C NACKED 5 times reading from slave', slave_addr)
                    return NACK, ""
            elif ex.args[0] == ETIMEDOUT:
                return TIMEOUT, ""
            else: 
                print('I2C Read Error', ex.args[0], slave_addr)       
                # raise ex
    
        except Exception as ex:
            raise ex("An error occurred reading from the I2C device")
