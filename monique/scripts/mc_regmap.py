from __future__ import division
import sys
import struct
from ctypes import c_uint8, c_uint16, c_int16


# Register Map motor I2C implementation
register_map = {
    'CONFIG_I2C':
    {'description': '''Default slave address of motor controller is 8.
                       SCL Loop out status is turned off.
                       Write to this register to set a unique address
                       and enable SCL loop out.''',
     'address': 0x00,
     'size': 1,
     'read only': False,
     'bit_fields': [('Slave Address', 'uint8_t', 7),
                    ('SCL Loop Out', 'bool', 1)],
     },

    'FLASH_CONFIG_READ':
    {'description': 'Encoder A settings stored in flash',
     'address': 0x01,
     'size': 42,
     'read only': True,
     'bit_fields': [('Encoder A Offset (Flash)', 'q12_t', 16),
                    ('Encoder A Gain (Flash)', 'q12_t', 16),
                    ('Encoder B Offset (Flash)', 'q12_t', 16),
                    ('Encoder B Gain (Flash)', 'q12_t', 16),
                    ('Encoder Datum Threshold (Flash)', 'q12_t', 16),
                    ('Encoder Phase Offset (Flash)', 'q12_t', 16),
                    ('Encoder Led Duty (Flash)', 'q12_t', 16),
                    ('Encoder Calibration Status (Flash)', 'q12_t', 16),
                    ('Current A Offset (Flash)', 'q12_t', 16),
                    ('Current A Gain (Flash)', 'q12_t', 16),
                    ('Current B Offset (Flash)', 'q12_t', 16),
                    ('Current B Gain (Flash)', 'q12_t', 16),
                    ('Current Kp (Flash)', 'q12_t', 16),
                    ('Current Ki (Flash)', 'q12_t', 16),
                    ('Motion Velocity Kp (Flash)', 'q12_t', 16),
                    ('Motion Velocity Ki (Flash)', 'q12_t', 16),
                    ('Motion Position Kp (Flash)', 'q12_t', 16),
                    ('Motion Position Ki (Flash)', 'q12_t', 16),
                    ('Motion Position Kd (Flash)', 'q12_t', 16),
                    ('Motion Knob Offset (Flash)', 'q12_t', 16),
                    ('Motor Phase Order (Flash)', 'q12_t', 16)]
     },

    
    'FLASH_CONFIG_WRITE':
    {'description': '''Writing to this register updates data stored in Flash
                       If both bit_fields are set Factory Reset takes precedence ''',
     'address': 0x02,
     'size': 1,
     'read only': False,
     'bit_fields': [('Save Options', 'uint8_t', 1)],  # 1 = registers, 2 = defaults
     },


    'SAMPLER_CHANNEL_TARGETS':
    {'description': 'Which Signals each channel is tracking',
     'address': 0x03,
     'size': 4,
     'read only': False,
     'bit_fields': [('Sampler Channel 1', 'sample_address', 8),
                    ('Sampler Channel 2', 'sample_address', 8),
                    ('Sampler Channel 3', 'sample_address', 8),
                    ('Sampler Channel 4', 'sample_address', 8)],
     },

    'SAMPLER_CHANNEL_ENABLE':
    {'description': 'Which channels the sampler is capturing',
     'address': 0x04,
     'size': 1,
     'read only': False,
     'bit_fields': [('Channel 1 Enable', 'bool', 1),
                    ('Channel 2 Enable', 'bool', 1),
                    ('Channel 3 Enable', 'bool', 1),
                    ('Channel 4 Enable', 'bool', 1)],
     },

    'SAMPLER_CH1_CH2_VALUE':
    {'description': 'Current value of Channels 1 & 2',
     'address': 0x05,
     'size': 4,
     'read only': True,
     'bit_fields': [('Channel 1 Value', 'int16_t', 16),
                    ('Channel 2 Value', 'int16_t', 16)],
     },

    'SAMPLER_ALL_CH_VALUE':
    {'description': 'Current value of all Channels',
     'address': 0x06,
     'size': 8,
     'read only': True,
     'bit_fields': [('Channel 1 Value', 'int16_t', 16),
                    ('Channel 2 Value', 'int16_t', 16),
                    ('Channel 3 Value', 'int16_t', 16),
                    ('Channel 4 Value', 'int16_t', 16)],
     },

    'SAMPLER_TRIGGER':
    {'description': 'Triggers Sample capturing',
     'address': 0x07,
     'size': 2,
     'read only': False,
     'bit_fields': [('Number of word samples to collect', 'int16_t', 16)]
     },

    'SAMPLER_STEP_RESPONSE':
    {'description': 'Triggers Sample capturing for step response',
     'address': 0x08,
     'size': 4,
     'read only': False,
     'bit_fields': [('Step Type', 'int16_t', 16),
                    ('Step Level', 'int16_t', 16)]
     },

    'SAMPLER_BUFFER_LEVEL':
    {'description': 'Triggers Sample capturing',
     'address': 0x09,
     'size': 2,
     'read only': True,
     'bit_fields': [('Number of samples available', 'int16_t', 16)]
     },

    'SAMPLER_BUFFER_READ':
    {'description': '''Window into sample buffer, auto increments after each read
                       Samples available(in SAMPLER_BUFFER_LEVEL reg) auto decrements after each read''',
     'address': 0x0A,
     'size': 16384,  
     'read only': True,
     'bit_fields': [('Sample Value N', 'int16_t', 16)],
     },

    'ENCODER_A_OFFSET':
    {'description': 'Offset adjustment for phototransistor A',
     'address': 0x0B,
     'size': 2,
     'read only': False,
     'bit_fields': [('Encoder A Offset', 'q12_t', 16)],
     },

    'ENCODER_A_GAIN':
    {'description': 'Gain adjustment for phototransistor A',
     'address': 0x0C,
     'size': 2,
     'read only': False,
     'bit_fields': [('Encoder A Gain', 'q12_t', 16)],
     },

    'ENCODER_B_OFFSET':
    {'description': 'Offset adjustment for phototransistor B',
     'address': 0x0D,
     'size': 2,
     'read only': False,
     'bit_fields': [('Encoder B Offset', 'q12_t', 16)],
     },

    'ENCODER_B_GAIN':
    {'description': 'Offset adjustment for phototransistor B',
     'address': 0x0E,
     'size': 2,
     'read only': False,
     'bit_fields': [('Encoder B Gain', 'q12_t', 16)],
     },

    'ENCODER_DATUM_THRESHOLD':
    {'description': 'Threshold for Datum dip',
     'address': 0x0F,
     'size': 2,
     'read only': False,
     'bit_fields': [('Encoder Datum Threshold', 'q12_t', 16)],
     },

    'ENCODER_PHASE_OFFSET':
    {'description': 'Offset between electical phase and encoder phase',
     'address': 0x10,
     'size': 2,
     'read only': False,
     'bit_fields': [('Encoder Phase Offset', 'q15_t', 16)],
     },

    'ENCODER_LED_DUTY':
    {'description': 'PWM Duty cycle of IR LED',
     'address': 0x11,
     'size': 2,
     'read only': False,
     'bit_fields': [('Encoder LED Duty', 'q9_t', 16)],
     },

    'ENCODER_CALIBRATION_STATUS':
    {'description': 'Indicate if encoder calibration has been done',
     'address': 0x12,
     'size': 2,
     'read only': False,
     'bit_fields': [('Encoder Calibration Status', 'int16_t', 16)]
                    #('Datum found', 'bool', 1),  # motor must be spun at startup to find datum
                    #('LED PWM Calibrated', 'bool', 1),
                    #('Encoder Gain & Offset Calibrated', 'bool', 1),
                    #('Encoder LUT Calibrated', 'bool', 1),
                    #('Phase Offset Calibrated', 'bool', 1),
                    #('Knob Offset Calibrated', 'bool', 1),
                    #('Datum LUT Programmed', 'bool', 1)],
     },

    'ENCODER_LUT_READ':
    {'description': '''Returns data in Encoder LUT Flash. ''',
     'address': 0x13,
     'size': 2048,
     'read only': True,
     'bit_fields': [('Encoder LUT value N', 'q15_t', 16)],
     },

    'ENCODER_LUT_WRITE':
    {'description': '''Writes data to Encoder LUT, Check device is ready before each write''',
     'address': 0x14,
     'size': 130,
     'read only': False,
     'bit_fields': [('Index', 'int16_t', 16),
                    ('Encoder LUT value N', 'q15_t', 16)],
     },

    'CURRENT_A_OFFSET':
    {'description': 'Offset Adjustment for current sense A signal',
     'address': 0x15,
     'size': 2,
     'read only': False,
     'bit_fields': [('Current A Offset', 'q12_t', 16)],
     },

    'CURRENT_A_GAIN':
    {'description': 'Gain Adjustment for current sense A signal',
     'address': 0x16,
     'size': 2,
     'read only': False,
     'bit_fields': [('Current A Gain', 'q12_t', 16)],
     },

    'CURRENT_B_OFFSET':
    {'description': 'Offset Adjustment for current sense B signal',
     'address': 0x17,
     'size': 2,
     'read only': False,
     'bit_fields': [('Current B Offset', 'q12_t', 16)],
     },

    'CURRENT_B_GAIN':
    {'description': 'Gain Adjustment for current sense B signal',
     'address': 0x18,
     'size': 2,
     'read only': False,
     'bit_fields': [('Current B Gain', 'q12_t', 16)],
     },

    'CURRENT_KP':
    {'description': 'Proportional term for current PI controller',
     'address': 0x19,
     'size': 2,
     'read only': False,
     'bit_fields': [('Current Kp', 'q12_t', 16)],
     },

    'CURRENT_KI':
    {'description': 'Intergral term for current PI controller',
     'address': 0x1A,
     'size': 2,
     'read only': False,
     'bit_fields': [('Current Ki', 'q12_t', 16)],
     },

    'MOTION_VELOCITY_KP':
    {'description': 'Proportional term for speed PI controller',
     'address': 0x1B,
     'size': 2,
     'read only': False,
     'bit_fields': [('Velocity Kp', 'q12_t', 16)],
     },

    'MOTION_VELOCITY_KI':
    {'description': 'Intergral term for speed PI controller',
     'address': 0x1C,
     'size': 2,
     'read only': False,
     'bit_fields': [('Velocity Ki', 'q12_t', 16)],
     },

    'MOTION_POSITION_KP':
    {'description': 'Proportional term for position PID controller',
     'address': 0x1D,
     'size': 2,
     'read only': False,
     'bit_fields': [('Position Kp', 'q12_t', 16)],
     },

    'MOTION_POSITION_KI':
    {'description': 'Proportional term for position PID controller',
     'address': 0x1E,
     'size': 2,
     'read only': False,
     'bit_fields': [('Position Ki', 'q12_t', 16)],
     },

    'MOTION_POSITION_KD':
    {'description': 'Proportional term for position PID controller',
     'address': 0x1F,
     'size': 2,
     'read only': False,
     'bit_fields': [('Position Kd', 'q12_t', 16)],
     },

    'MOTION_POSITION_OFFSET':
    {'description': '''Angle offset between knob zero position and
                       encoder datum position - needs to be calibrated manually ''',
     'address': 0x20,
     'size': 2,
     'read only': False,
     'bit_fields': [('Knob Offset', 'q12_t', 16)],
     },

    'MOTION_HAPTIC_CONFIG':
    {'description': 'Haptic Configuration data for viscous friction, number of detents and detent strength',
     'address': 0x21,
     'size': 7,
     'read only': False,
     'bit_fields': [('Viscous Friction', 'uint8_t', 8),
                    ('Detent Number', 'uint8_t', 8),
                    ('Detent Strength', 'uint8_t', 8),
                    ('Left Barrier Pos', 'int16_t', 16),
                    ('Right Barrier Pos', 'int16_t', 16)],
     },


    'HAPTIC_LUT_READ':
    {'description': '''Window into Haptic LUT. Auto increments
                       Must call 1024 times in a row to write
                       Must call 1024 times in a row to read''',
     'address': 0x22,
     'size': 2048,
     'read only': True,
     'bit_fields': [('HAPTIC LUT value', 'q15_t', 16)],
     },

    'HAPTIC_LUT_WRITE':
    {'description': '''Writes data to Haptic LUT, Check device is ready before each write''',
     'address': 0x23,
     'size': 130,
     'read only': False,
     'bit_fields': [('Index', 'int16_t', 16),
                    ('Encoder LUT value N', 'q15_t', 16)],
     },

    'MOTION_MODE_OPENLOOP':
    {'description': '''Writing to this register puts motion controller into openloop mode.
                       Useful for calibrating encoder and finding datum at startup.
                       Writing zero to this register will stop the motor (All phases of bridge pulled low)
                         - Duty: range 0 to 255  (Percent PWM duty cycle)
                         - Step Size: range -128 to 127 (Phase angle step per current loop)
                            Current loop runs at 20.833kHz [125kHz PWM freq / 6].
                            1 step = 0.001569 mechanical degrees [360(degrees)/7(pole pairs)/32768(Q15_CIRCLE)]
                                   = 5.45 RPM [0.001569(degrees)*20833(loop freq)/360(degrees)*60(seconds)]
                          127 step = 692.10 RPM
                         -128 step = 697.54 RPM ''',
     'address': 0x24,
     'size': 4,
     'read only': False,
     'bit_fields': [('Openloop duty', 'q12_t', 16),
                    ('Openloop step size', 'int16_t', 16)],
     },

    'MOTION_MODE_FIND_DATUM':
    {'description': '''Spins Motor until datum to found, Read calibration status after to confirm''',
     'address': 0x25,
     'size': 0,
     'read only': False,
     'bit_fields': [],
     },

    'MOTION_MODE_PHASE_ANGLE':
    {'description': '''Spins Motor until datum to found, Read calibration status after to confirm''',
     'address': 0x26,
     'size': 4,
     'read only': False,
     'bit_fields': [('Duty', 'q12_t', 16),
                    ('Angle', 'q15_t', 16)],
     },

    'MOTION_MODE_CURRENT':
    {'description': '''Writing to this register puts motion controller into Current mode
                       (closed loop) PI Current Loop -> Motor.
                         - Current: range -2048 to 2048 (% of max current, positive is CW)
                         - Value Error: Set by hardware when out of range value received
                       Writes with out of range values will be ignored and motion controller mode
                       will be unchanged''',
     'address': 0x27,
     'size': 2,
     'read only': False,
     'bit_fields': [('Target Current', 'int16_t', 16)],
     },

    'MOTION_MODE_SPEED':
    {'description': '''Writing to this register puts motion controller into Speed mode
                        (closed loop) PI Speed loop -> PI Current Loop -> Motor.
                         - Speed: range -1024 to 1023 (RPM, positive is CW)
                         - Value Error: Set by hardware when out of range value received
                       Writes with out of range values will be ignored and motion controller mode
                       will be unchanged''',
     'address': 0x28,
     'size': 2,
     'read only': False,
     'bit_fields': [('Target Velocity', 'int16_t', 16)],
     },

    'MOTION_MODE_POSITION':
    {'description': '''Writing to this register puts motion controller into Current mode
                       (closed loop) PID Position Loop -> PI Current Loop -> Motor.
                         - position: range 0 to 32767 (bottom bits are noisy. Best to use top 10 bits)
                         - Value Error: Set by hardware when out of range value received
                       Writes with out of range values will be ignored and motion controller mode
                       will be unchanged''',
     'address': 0x29,
     'size': 2,
     'read only': False,
     'bit_fields': [('Target Position', 'int16_t', 16)],
     },

    'MOTION_MODE_HAPTIC':
    {'description': '''Writing to this register puts motion controller into Haptic mode
                       (closed loop) Haptic Loop -> PI Current Loop -> Motor.
                         - Haptic preset: range 0 to 255
                         - Value Error: Set by hardware when out of range value received
                       Writes with out of range values will be ignored and motion controller mode will be unchanged''',
     'address': 0x2A,
     'size': 1,
     'read only': False,
     'bit_fields': [('Haptic Preset', 'uint8_t', 8)],
     },

    'MOTOR_STATUS':
    {'description': 'Motion Controller current mode of operation',
     'address': 0x2B,
     'size': 4,
     'read only': True,
     'bit_fields': [('Knob Position', 'int16_t', 16),
                    ('Knob State', 'int16_t', 16)],
     },

    'COG_LUT_READ':
    {'description': '''Returns data in Cog LUT Flash. ''',
     'address': 0x2C,
     'size': 1792,
     'read only': True,
     'bit_fields': [('Encoder LUT value N', 'q15_t', 16)],
     },

    'COG_LUT_WRITE':
    {'description': '''Writes data to Encoder LUT, Check device is ready before each write''',
     'address': 0x2D,
     'size': 10,
     'read only': False,
     'bit_fields': [('Index', 'int16_t', 16),
                    ('Cog LUT value index', 'q15_t', 16),
                    ('Cog LUT value index+1', 'q15_t', 16),
                    ('Cog LUT value index+2', 'q15_t', 16),
                    ('Cog LUT value index+3', 'q15_t', 16)],
     },

    'MOTOR_PHASE_ORDER':
    {'address': 0x2E,
     'size': 1,
     'read only': False,
     'bit_fields': [('Phase Swap', 'uint8_t', 8)],
     },

    'REBOOT':
    {'address': 0x2F,
     'size': 1,
     'read only': False,
     'bit_fields': [('Reboot', 'uint8_t', 8)],
     },

    'ENCODER_MIN_MAX':
    {'description': '',
     'address': 0x30,
     'size': 8,
     'read only': True,
     'bit_fields': [('Encoder A min', 'int16_t', 16),
                    ('Encoder A max', 'int16_t', 16),
                    ('Encoder B min', 'int16_t', 16),
                    ('Encoder B max', 'int16_t', 16)]
     }, 

    'CAL_ENC_PARAMS':
    {'description': '''Spins Motor and finds encoder params''',
     'address': 0x33,
     'size': 1,
     'read only': False,
     'bit_fields': [],
     },     
}

# Generate a dictionary to look up bit fields index when reading data
bit_field = dict()
for key in register_map:
    bit_fields = list(register_map[key]['bit_fields'])
    for field in bit_fields:
        bit_field[field[0]] = bit_fields.index(field)
reg_type = 1
reg_value = 2


# sample channel address enum
sample_address = {
    # Openloop
    'Openloop Angle': 0,
    'Openloop Duty': 1,
    # Encoder
    'Encoder A': 2,
    'Encoder B': 3,
    'Phase Sector': 4,
    'Encoder Sector': 5,
    'Encoder Angle (RAW)': 6,
    'Encoder Angle (LUT)': 7,
    'Corrected Phase': 8,
    'Phase Angle': 9,
    # Current Control
    'Current A': 10,
    'Current B': 11,
    'Id': 12,
    'Iq': 13,
    'Flux Target': 14,
    'Flux Error': 15,
    'Vflux': 16,
    'Torque Target': 17,
    'Torque Error': 18,
    'Vtorque': 19,
    'enc_a_raw': 20,
    'enc_b_raw': 21,
    'enc_a_gain': 22,
    'enc_b_gain': 23,
    'Valpha': 24,
    'Vbeta': 25,
    'Duty A': 26,
    'Duty B': 27,
    'Duty C': 28,
    # Motion Control
    'Motion Position': 29,
    'Motion Velocity': 30,
    'Knob Position': 31,
    'Barrier Penetration': 32,
    'Friction Torque': 33,
    'Detent Torque': 34,
    'Impulse Torque': 35,
    'Velocity Target': 36,
    'Velocity Error': 37,
    'Velocity P term': 38,
    'Velocity I term': 39,
    'Position Target': 40,
    'Position Error': 41,
    'Position P term': 42,
    'Position I term': 43,
    'Position D term': 44,
    'Step Level': 45,
    'Vbus': 46
}

address_name = list(sample_address)
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
        # Special case for LUT writes
        if register in  ['ENCODER_LUT_WRITE', 'HAPTIC_LUT_WRITE']:
            # Check the params length is valid
            if len(params) != 2:
                raise ValueError('2 fields required for register {}'.format(register))

            # Get the LUT index (2 bytes)
            if sys.version_info.major == 3:
                reg_data = int(params[0]).to_bytes(2, 'little').hex()
            else:
                reg_data = to_bytes(params[0], 2, 'little').encode('hex')            
            
            # Get the LUT and check the size
            lut_data = params[1]
            size = register_map[register]['size']
            if len(lut_data) != ((size-2)/2):
                raise ValueError('Param requires {} values for register {}'.format(((size-2)/2), register))

            # Process each LUT entry as a word
            for p in lut_data:
                if sys.version_info.major == 3:
                    reg_data += int(p).to_bytes(2, 'little').hex()
                else:
                    reg_data += to_bytes(int(p), 2, 'little').encode('hex')
        else:
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
                    if field[typedef] == 'sample_address':
                        data |= (sample_address[params[index]] & bit_mask) << bit_shift
                    else:
                        data |= (params[index] & bit_mask) << bit_shift
                    bit_shift += field[width]
                    index += 1
                if (register in  ['SAMPLER_CHANNEL_TARGETS', 'MOTION_MODE_OPENLOOP',
                                'MOTION_MODE_PHASE_ANGLE', 'MOTION_MODE_POSITION',
                                'MOTION_HAPTIC_CONFIG', 'COG_LUT_WRITE',
                                'ENCODER_CALIBRATION_STATUS']):
                    if sys.version_info.major == 3:
                        reg_data = data.to_bytes(register_map[register]['size'], 'little').hex()
                    else:
                        reg_data = to_bytes(data, register_map[register]['size'], 'little').encode('hex')
                else:
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
    if len(data_buffer) >> 1 != expected_bytes:
        raise ValueError('Expected {} bytes, Read{}'
                         .format(expected_bytes, len(data_buffer)))
    unpacked_data = int(data_buffer, 16)
    bit_shift = expected_bytes * 8
    if (register == 'SAMPLER_CHANNEL_ENABLE'):
        bit_shift -= 4
    data = []
    for field in register_map[register]['bit_fields']:
        bit_shift -= field[width]
        bit_mask = (1 << field[width])-1
        if field[typedef] in ('q9_t', 'q12_t', 'q15_t', 'int16_t'):
            data.append([field[name], field[typedef], swap16((unpacked_data >> bit_shift & bit_mask))])
        elif field[typedef] == 'sample_address':
            data.append([field[name], field[typedef], address_name[(unpacked_data >> bit_shift) & bit_mask]])
        else:
            data.append([field[name], field[typedef], (unpacked_data >> bit_shift) & bit_mask])
    if len(data) == 1:
        return data[0]
    else:
        return data


def swap16(x):
    if sys.version_info.major == 3:
        return int.from_bytes(x.to_bytes(2, byteorder='little'), byteorder='big', signed=True)
    else:
        return (((x << 8) & 0xFF00) | ((x >> 8) & 0x00FF))

def to_bytes(n, length, byteorder='big'):
    h = '%x' % n
    s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
    return s if byteorder == 'big' else s[::-1]
