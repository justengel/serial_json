

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


def time_numpy_array(test_runs=1000):
    import timeit
    import numpy as np
    import json
    import serial_json
    import serial_json.bytes_support   # Not needed in normal use
    import serial_json.numpy_support   # Not needed in normal use

    n = np.array([(1.2, 2.3, 3.4, 4.5),
                  (5.6, 6.7, 7.8, 8.9)] * 100, dtype=np.dtype('<f4'))
    # n_list = json.dumps(n.tolist())
    # n_serial = serial_json.dumps(n)

    def run_serial_json():
        serial_json.dumps(n)

    def run_list():
        json.dumps(n.tolist())

    t1 = timeit.timeit(run_serial_json, number=test_runs)
    print('Serial JSON DUMPS (size {}): '.format(n.size), t1)
    t2 = timeit.timeit(run_list, number=test_runs)
    print('List JSON DUMPS (size {}): '.format(n.size), t2)

    # ===== Larger size =====
    n = np.array([(1.2, 2.3, 3.4, 4.5),
                  (5.6, 6.7, 7.8, 8.9)] * 10000, dtype=np.dtype('<f4'))
    # n_list = json.dumps(n.tolist())
    # n_serial = serial_json.dumps(n)

    def run_serial_json():
        serial_json.dumps(n)

    def run_list():
        json.dumps(n.tolist())

    t1 = timeit.timeit(run_serial_json, number=test_runs)
    print('Serial JSON DUMPS (size {}): '.format(n.size), t1)
    t2 = timeit.timeit(run_list, number=test_runs)
    print('List JSON DUMPS (size {}): '.format(n.size), t2)

    # ===== str to numpy =====
    n = np.array([(1.2, 2.3, 3.4, 4.5),
                  (5.6, 6.7, 7.8, 8.9)] * 10000, dtype=np.dtype('<f4'))
    n_list = json.dumps(n.tolist())
    n_serial = serial_json.dumps(n)

    def run_serial_json():
        serial_json.loads(n_serial)

    def run_list():
        np.array(json.loads(n_list))

    t1 = timeit.timeit(run_serial_json, number=test_runs)
    print('Serial JSON LOADS (size {}): '.format(n.size), t1)
    t2 = timeit.timeit(run_list, number=test_runs)
    print('List JSON LOADS (size {}): '.format(n.size), t2)


def time_np_recarray(test_runs=1000):
    import timeit
    import numpy as np
    import json
    import serial_json
    import serial_json.bytes_support   # Not needed in normal use
    import serial_json.numpy_support   # Not needed in normal use

    dtype = np.dtype([('a', '<i4'), ('b', '<f4'), ('c', '<u1'), ('d', '|O')])
    n = np.recarray((100,), dtype=dtype)
    # n_list = json.dumps(n.tolist())
    # n_serial = serial_json.dumps(n)

    def run_serial_json():
        serial_json.dumps(n)

    def run_list():
        json.dumps(n.tolist())

    t1 = timeit.timeit(run_serial_json, number=test_runs)
    print('Serial JSON DUMPS (size {}): '.format(n.size), t1)
    t2 = timeit.timeit(run_list, number=test_runs)
    print('List JSON DUMPS (size {}): '.format(n.size), t2)

    dtype = np.dtype([('a', '<i4'), ('b', '<f4'), ('c', '<u1'), ('d', '|O')])
    n = np.recarray((10000,), dtype=dtype)
    n_list = json.dumps(n.tolist())
    n_serial = serial_json.dumps(n)

    def run_serial_json():
        serial_json.dumps(n)

    def run_list():
        json.dumps(n.tolist())

    t1 = timeit.timeit(run_serial_json, number=test_runs)
    print('Serial JSON DUMPS (size {}): '.format(n.size), t1)
    t2 = timeit.timeit(run_list, number=test_runs)
    print('List JSON DUMPS (size {}): '.format(n.size), t2)

    # ===== str to numpy =====
    dtype = np.dtype([('a', '<i4'), ('b', '<f4'), ('c', '<u1'), ('d', '|O')])
    n = np.recarray((10000,), dtype=dtype)
    n_list = json.dumps(n.tolist())
    n_serial = serial_json.dumps(n)

    def run_serial_json():
        serial_json.loads(n_serial)

    def run_list():
        li = json.loads(n_list)
        arr = np.recarray((len(li)), dtype=dtype)

        for i, v in enumerate(li):
            arr[dtype.names[0]][i] = v[0]
            arr[dtype.names[1]][i] = v[1]
            arr[dtype.names[2]][i] = v[2]
            arr[dtype.names[3]][i] = v[3]

    t1 = timeit.timeit(run_serial_json, number=test_runs)
    print('Serial JSON LOADS (size {}): '.format(n.size), t1)
    t2 = timeit.timeit(run_list, number=test_runs)
    print('List JSON LOADS (size {}): '.format(n.size), t2)


if __name__ == '__main__':
    test_ndarray()
    test_np_structured_array()
    test_np_recarray()

    time_numpy_array()
    time_np_recarray()

    print('All tests finished successfully!')
