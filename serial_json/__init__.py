from serial_json.interface import Message, Serializer, register, unregister, get_serializer, dumps, dump, loads, load, \
    default, object_hook

try:
    import serial_json.bytes_support
except (ImportError, Exception):
    pass

try:
    import serial_json.datetime_support
    TIME_FORMATS = serial_json.datetime_support.TIME_FORMATS
    DATE_FORMATS = serial_json.datetime_support.DATE_FORMATS
    DATETIME_FORMATS = serial_json.datetime_support.DATETIME_FORMATS
    make_time = serial_json.datetime_support.make_time
    make_date = serial_json.datetime_support.make_date
    make_datetime = serial_json.datetime_support.make_datetime
except (ImportError, Exception):
    TIME_FORMATS = []
    DATE_FORMATS = []
    DATETIME_FORMATS = []

    def make_time(*args, **kwargs):
        raise EnvironmentError('Could not properly setup datetime utilities.')

    def make_date(*args, **kwargs):
        raise EnvironmentError('Could not properly setup datetime utilities.')

    def make_datetime(*args, **kwargs):
        raise EnvironmentError('Could not properly setup datetime utilities.')


try:
    import serial_json.numpy_support
except (ImportError, Exception):
    pass
