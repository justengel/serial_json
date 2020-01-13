from serial_json.interface import register


def bytes_to_str(bts):
    return bts.decode('latin1')


def bytes_from_str(bts):
    return bts.encode('latin1')


register(bytes, bytes_to_str, bytes_from_str)
