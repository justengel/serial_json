import ast
import numpy as np
from serial_json.interface import register


__all__ = ['np_to_dict', 'np_from_dict', 'rec_from_dict']


def np_to_dict(obj):
    """Convert a numpy array to a json serializable dictionary."""
    dtype = str(obj.dtype)
    if getattr(obj.dtype, 'names', None) is not None:
        dtype = str(obj.dtype.descr)  # Record array and structured array support
    return {'data': bytes(obj.data),  # REQUIRES bytes_support!
            'shape': ','.join((str(i) for i in obj.shape)), 'dtype': dtype}


def np_from_dict(obj):
    """Convert a json dictionary to a numpy array."""
    byts = obj.get('data', b'')
    shape = tuple(int(i) for i in obj.get('shape', '-1').split(','))
    dtype = obj.get('dtype', '<f4')
    try:
        dtype = ast.literal_eval(dtype)
    except (ValueError, TypeError, Exception):
        pass
    dtype = np.dtype(dtype)

    # Create an array and override the memoryview
    arr = np.empty(shape, dtype=dtype)
    arr.data = byts
    return arr


def rec_from_dict(obj):
    """Convert a json dictionary to a numpy record array."""
    return np_from_dict(obj).view(np.recarray)


register(np.ndarray, np_to_dict, np_from_dict)
register(np.recarray, np_to_dict, rec_from_dict)  # Record array support
