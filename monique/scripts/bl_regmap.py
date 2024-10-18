from __future__ import division
import sys
import struct
from ctypes import c_bool, c_uint8, c_uint32


# Register Map for bootloader
register_map = {
    'CONFIG_I2C':
    {'description': '''Default slave address of motor controller is 8.
                       Default slave address of front panel controller is 100.
                       SCL Loop out is turned off. (only applies to motor)

                       For motor controllers write to this register to set a unique
                       address and enable SCL loop out so downstream devices can be
                       configured.''',
     'address': 0x00,
     'size': 1,
     'read only': False,
     'bit_fields': [('Slave Address', 'uint8_t', 7),
                    ('SCL Loop Out', 'bool', 1)],
     },


    'CHECK_FIRMWARE': 
    {'description': '''Adjust Vector Table offset and start app.''',
     'address': 0x01,
     'size': 16,
     'read only': True,
     'bit_fields': [('Firmware Type', 'firmware_t', 8),
                    ('Version Major', 'uint8', 8),
                    ('Version Minor', 'uint8', 8),
                    ('Version Patch', 'uint8', 8),
                    ('Size', 'uint32', 32),
                    ('Tag', 'str', 64)],                
     },

    'START_FIRMWARE':
    {'description': '''Adjust Vector Table offset and start app.''',
     'address': 0x02,
     'size': 1,
     'read only': False,
     'bit_fields': [('Ignore Header', 'uint8', 8)], 
     },

    'START_PROGRAMMING':
    {'description': '''Set starting Address and number of bytes for firmware
                       check status register before sending data''',
     'address': 0x03,
     'size': 8,
     'bit_fields': [('Size (bytes)', 'uint32_t', 32),  
                    ('Flash Offset', 'uint32_t', 32)],
     },

    'WRITE_FIRMWARE':
    {'description': '''Writes one intel hex data record to flash
                       check status register after each write, status will be either''',
     'address': 0x04,
     'size': 20,
     'bit_fields': [('data', 'bytes', 128),
                    ('address', 'uint32_t', 32)],
     }
}

bit_field = dict()
for key in register_map:
    bit_fields = list(register_map[key]['bit_fields'])
    for field in bit_fields:
        bit_field[field[0]] = bit_fields.index(field)

status_t = ['IDLE',
            'BUSY',
            'PARAM_SIZE_ERROR',
            'FIRMWARE_OK',
            'INVALID_FIRMWARE',
            'INVALID_ADDRESS',
            'READY_FOR_DATA',
            'CHECKSUM_ERROR',
            'PROGRAMMING_COMPLETE'
            ]

name = 0
typedef = 1
width = 2


def encode(register, params=[]):
    ''' Encodes control register address and params based on register mapping table.
        returns: message as a hex string
    '''
    if register not in register_map:
        raise ValueError('{} not in register map'
                         .format(register))
    if sys.version_info.major == 3:                         
        reg_address = register_map[register]['address'].to_bytes(1, 'big').hex()
    else:
        reg_address = to_bytes(register_map[register]['address'], 1, 'big').encode('hex')
    reg_data = None

    if len(params):
        bit_fields = register_map[register]['bit_fields']
        if (bit_fields is not None):
            if len(params) != len(bit_fields):
                raise ValueError('{} fields required for register {}'
                                 .format(len(bit_fields), register))
            index = 0
            bit_shift = 0
            data = 0
            for field in bit_fields:
                bit_mask = (1 << field[width])-1
                data |= (params[index] & bit_mask) << bit_shift
                bit_shift += field[width]
                index += 1
            if sys.version_info.major == 3: 
                reg_data = data.to_bytes(register_map[register]['size'], 'big').hex()
            else:
                reg_data = to_bytes(data, register_map[register]['size'], 'big').encode('hex')
        
    if (reg_data):
        return (reg_address + reg_data)
    else:
        return reg_address


def decode(register, data_buffer):
    ''' Decodes data based on bitfields in regmap. Data buffer expected to be in hex string format '''
    # print('data', data_buffer)
    if register not in register_map:
        raise ValueError('{} not in register map'
                         .format(register))
    expected_bytes = register_map[register]['size']
    if len(data_buffer)>>1 != expected_bytes:
        raise ValueError('Expected {} bytes, Read{}'
                         .format(expected_bytes, len(data_buffer)))
    unpacked_data = int(data_buffer, 16)
    bit_shift = expected_bytes * 8
    data = []
    for field in register_map[register]['bit_fields']:
        bit_shift -= field[width]
        bit_mask = (1 << field[width])-1
        if field[typedef] == 'firmware_t':
            firmware_t = (unpacked_data >> bit_shift) & bit_mask
            if firmware_t == 1:
                firmware_t = 'Motor'
            elif firmware_t == 2:
                firmware_t = 'Panel'
            else:
                firmware_t = 'None'
            data.append([field[name], field[typedef], firmware_t])
        elif field[typedef] == 'uint32':
            fw_size = (unpacked_data >> bit_shift) & bit_mask
            fw_size = int.from_bytes(fw_size.to_bytes(4, byteorder='little'), byteorder='big', signed=False)
            data.append([field[name], field[typedef], fw_size])
        elif field[typedef] == 'str':
            tag = (unpacked_data >> bit_shift) & bit_mask
            try:
                tag = tag.to_bytes(8, byteorder='big').decode('utf-8').strip()
            except UnicodeDecodeError:
                tag = 'Invalid'
                #print('Invalid firmware tag')
            data.append([field[name], field[typedef], tag])
        else:
            data.append([field[name], field[typedef], (unpacked_data >> bit_shift) & bit_mask])
    return data


def get_reg_address(register):
    return struct.pack('>B', register_map[register]['address'])


def get_reg_bytes(register):
    return register_map[register]['size'] >> 3


def to_bytes(n, length, endianess='big'):
    h = '%x' % n
    s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
    return s if endianess == 'big' else s[::-1]
