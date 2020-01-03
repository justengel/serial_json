

def test_bytes():
    import serial_json
    import serial_json.bytes_support   # Not needed in normal use

    bts = b'12345'
    assert serial_json.loads(serial_json.dumps(bts)) == bts


if __name__ == '__main__':
    test_bytes()

    print('All tests finished successfully!')
