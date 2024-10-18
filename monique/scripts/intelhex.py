def calculate_checksum(record):
    hex_record = (record['length'].to_bytes(1, 'big').hex()
                  + record['address']
                  + record['type']
                  + record['data']
                  )
    byte_record = bytes.fromhex(hex_record)
    checksum = 0
    for b in byte_record:
        checksum += b
    return 256-(checksum & 0xff) & 0xff


def parse_hex(filename):
    records = []
    with open(filename, 'r') as hexfile:
        for line in hexfile:
            line = line.strip('\n')
            if (line[0] == ':'):  # every Intel Hex record starts with a colon
                hex_record = bytes.fromhex(line[1:])
                length = int.from_bytes(hex_record[0:1], 'big')
                if (length == len(hex_record) -5):
                    address = hex_record[1:3] 
                    rec_type = hex_record[3:4]
                    data = hex_record[4:4+length]
                    checksum = 0
                    for b in hex_record[0:-1]:
                        checksum += b
                    checksum = 256-(checksum & 0xff) & 0xff
                    if (checksum != hex_record[-1:][0]):
                        print(line)
                        print(checksum, hex_record[-1:][0])
                        raise ValueError('Checksum Mismatch')
                else:
                    raise ValueError('Length of Intel Hex record incorrect')
            else:
                raise ValueError('Intel Hex record did not begin with a colon')
            records.append({
                'length': length, 
                'address': address.hex().upper(),
                'type': rec_type.hex().upper(),
                'data': data.hex().upper(),
                'checksum': hex_record[-1:].hex().upper()
            })
        return records


def get_start_address(records):
    return records[0]['data'] + records[1]['address']


def get_data_size(records):
    size = 0
    for record in records:
        if record['type'] == '00':
            size += record['length']
    return size


def pad_data_records(records):
    print('Padding data records to 16 bytes')
    for record in records:
        if record['type'] == '00':
            if record['length'] != 16:
                addr = record['address']
                data = record['data']
                data += 'F' * (32 - len(data))
                modify_record(records, addr, data)


def modify_record(records, addr, data):
    new_record = { 
        'length': len(data)//2,  # two hex values = 1 byte
        'address': addr,
        'type': '00',
        'data': data,
        'checksum': '00'
    }
    new_record['checksum'] = calculate_checksum(new_record).to_bytes(1, 'big').hex().upper()
    index = 0
    for record in records:
        if record['address'] == addr:
            print('Modify record at address 0x{} from'.format(addr))
            print('  ', record, 'to')
            print('  ', new_record)
            records[index] = new_record
            break
        index += 1


def write_fw_hdr(records, fw_type, version, data_size, tag):
    print('Inserting {} firmware header version {}, {}, {} data bytes'.format(fw_type, version, tag, data_size))
    tag = bytes(tag, 'ascii')
    tag += b'0' * (8 - len(tag))
    ver_major, ver_minor, ver_patch = version.split('.')
    if (fw_type == 'CONTROL_SURFACE'):
        fw_type = 2
    elif (fw_type == 'MOTOR_CONTROLLER'):
        fw_type = 1
    else:
        raise ValueError('Unknown firmware type {}'.format(fw_type))
    data = (fw_type.to_bytes(1, 'big').hex().upper()
            + int(ver_major).to_bytes(1, 'big').hex().upper()
            + int(ver_minor).to_bytes(1, 'big').hex().upper()
            + int(ver_patch).to_bytes(1, 'big').hex().upper()
            + data_size.to_bytes(4, 'little').hex().upper()
            + tag.hex().upper()
            )
    modify_record(records, '10C0', data)
