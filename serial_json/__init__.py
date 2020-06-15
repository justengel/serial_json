from serial_json.interface import Serializer, register, unregister, get_serializer, \
    base_create_object, RegisterMetaclass, \
    dumps, dump, loads, load, default, object_hook

from .dataclasses import MISSING, field, field_property, DataclassMeta, DataClass, dataclass, Message

try:
    import serial_json.bytes_support
except (ImportError, Exception):
    pass

try:
    import serial_json.datetime_support
    DATE_FORMATS = serial_json.datetime_support.DATE_FORMATS
    TIME_FORMATS = serial_json.datetime_support.TIME_FORMATS
    DATETIME_FORMATS = serial_json.datetime_support.DATETIME_FORMATS
    make_date = serial_json.datetime_support.make_date
    make_time = serial_json.datetime_support.make_time
    make_datetime = serial_json.datetime_support.make_datetime
    str_date = serial_json.datetime_support.str_date
    str_time = serial_json.datetime_support.str_time
    str_datetime = serial_json.datetime_support.str_datetime

    date_property = serial_json.datetime_support.date_property
    time_property = serial_json.datetime_support.time_property
    datetime_property = serial_json.datetime_support.datetime_property
    timedelta_attr_property = serial_json.datetime_support.timedelta_attr_property
    seconds_property = serial_json.datetime_support.seconds_property

except (ImportError, Exception):
    DATE_FORMATS = []
    TIME_FORMATS = []
    DATETIME_FORMATS = []

    def make_date(*args, **kwargs):
        raise EnvironmentError('Could not properly setup datetime utilities.')

    make_time = make_date
    make_datetime = make_date
    str_date = make_date
    str_time = make_date
    str_datetime = make_date

    date_property = make_date
    time_property = make_date
    datetime_property = make_date
    timedelta_attr_property = make_date
    seconds_property = make_date

try:
    from serial_json.weekdays_list import Weekdays, weekdays_property, weekdays_attr_property
except (ImportError, Exception):
    class Weekdays:
        def __new__(cls, *args, **kwargs):
            raise EnvironmentError('Could not properly setup weekday utilities.')

    def weekdays_attr_property(*args, **kwargs):
        raise EnvironmentError('Could not properly setup weekday utilities.')

    def weekdays_property(*args, **kwargs):
        raise EnvironmentError('Could not properly setup weekday utilities.')


try:
    from serial_json.numpy_support import np_to_dict, np_from_dict, rec_from_dict
except (ImportError, Exception):
    def np_to_dict(*args, **kwargs):
        raise EnvironmentError('Could not properly setup numpy utilities.')

    def np_from_dict(*args, **kwargs):
        raise EnvironmentError('Could not properly setup numpy utilities.')

    def rec_from_dict(*args, **kwargs):
        raise EnvironmentError('Could not properly setup numpy utilities.')
