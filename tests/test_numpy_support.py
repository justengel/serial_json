

def test_ndarray():
    import numpy as np
    import serial_json
    import serial_json.bytes_support   # Not needed in normal use
    import serial_json.numpy_support   # Not needed in normal use

    n = np.array([(1, 2, 3, 4),
                  (5, 6, 7, 8)], dtype=np.dtype('<i4'))
    obj = serial_json.loads(serial_json.dumps(n))
    assert type(obj) == type(n)
    assert np.all(obj == n)
    assert obj.dtype == n.dtype
    assert obj.shape == n.shape

    n = np.array([(1.2, 2.3, 3.4, 4.5),
                  (5.6, 6.7, 7.8, 8.9)], dtype=np.dtype('<f4'))
    obj = serial_json.loads(serial_json.dumps(n))
    assert type(obj) == type(n)
    assert np.all(obj == n)
    assert obj.dtype == n.dtype
    assert obj.shape == n.shape


def test_np_structured_array():
    import numpy as np
    import serial_json
    import serial_json.bytes_support   # Not needed in normal use
    import serial_json.numpy_support   # Not needed in normal use

    n = np.array([(1, 2.3, True, 'abc'),
                  (5, 6.7, False, 'def')],
                 dtype=np.dtype([('a', '<i4'), ('b', '<f4'), ('c', '<u1'), ('d', '|O')]))
    obj = serial_json.loads(serial_json.dumps(n))
    assert type(obj) == type(n)
    assert np.all(obj == n)
    assert obj.dtype == n.dtype
    assert obj.shape == n.shape


def test_np_recarray():
    import numpy as np
    import serial_json
    import serial_json.bytes_support   # Not needed in normal use
    import serial_json.numpy_support   # Not needed in normal use

    n = np.recarray((2,), dtype=np.dtype([('a', '<i4'), ('b', '<f4'), ('c', '<u1'), ('d', '|O')]))
    n[0] = (1, 2.3, True, 'abc')
    n[1] = (5, 6.7, False, 'def')
    obj = serial_json.loads(serial_json.dumps(n))
    assert type(obj) == type(n)
    assert np.all(obj == n)
    assert obj.dtype == n.dtype
    assert obj.shape == n.shape


if __name__ == '__main__':
    test_ndarray()
    test_np_structured_array()
    test_np_recarray()

    print('All tests finished successfully!')
