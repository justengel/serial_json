import datetime
from typing import Union, List
from serial_json.interface import register
from serial_json.dataclasses import MISSING, field_property


__all__ = ['DATE_FORMATS', 'TIME_FORMATS', 'DATETIME_FORMATS',
           'make_date', 'make_time', 'make_datetime', 'str_date', 'str_time', 'str_datetime',
           'date_property', 'time_property', 'datetime_property', 'timedelta_attr_property', 'seconds_property']


DATE_FORMATS = [
    '%Y-%m-%d', '%m/%d/%Y',   # '2019-04-17', '04/17/2019'
    '%b %d %Y', '%b %d, %Y',  # 'Apr 17 2019', 'Apr 17, 2019'
    '%d %b %Y', '%d %b, %Y',  # '17 Apr 2019', '17 Apr, 2019'
    '%B %d %Y', '%B %d, %Y',  # 'April 17 2019', 'April 17, 2019'
    '%d %B %Y', '%d %B, %Y',  # '17 April 2019', '17 April, 2019'
    ]

TIME_FORMATS = [
    '%I:%M:%S %p',     # '02:24:55 PM'
    '%I:%M:%S.%f %p',  # '02:24:55.000200 PM'
    '%I:%M %p',        # '02:24 PM'
    '%H:%M:%S',        # '14:24:55'
    '%H:%M:%S.%f',     # '14:24:55.000200'
    '%H:%M',           # '14:24'
    ]

DATETIME_FORMATS = [d + ' ' + t for t in TIME_FORMATS for d in DATE_FORMATS] + DATE_FORMATS + TIME_FORMATS


def make_date(date_string, formats=None):
    """Make the date object from the given time string.

    Args:
        date_string (str): Date string 'mm/dd/yyyy' ...
        formats (list): List of acceptable time string formats.

    Returns:
        d (datetime.date): Date object or None.
    """
    if isinstance(date_string, datetime.date):
        return date_string

    if formats is None:
        formats = DATETIME_FORMATS

    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(date_string, fmt)
            return dt.date()
        except (TypeError, ValueError, Exception):
            pass

    try:  # Try ISO format
        return datetime.datetime.fromisoformat(date_string)
    except:
        pass

    raise ValueError('Invalid date format {}. Allowed formats are {}'.format(repr(date_string), repr(formats)))


def make_time(time_string, formats=None):
    """Make the time object from the given time string.

    Args:
        time_string (str): Time string '04:00 PM' ...
        formats (list): List of acceptable time string formats.

    Returns:
        t (datetime.time): Time object or None.
    """
    if isinstance(time_string, datetime.time):
        return time_string

    if formats is None:
        formats = DATETIME_FORMATS

    for fmt in formats:
        try:
            dt = datetime.datetime.strptime(time_string, fmt)
            return dt.time()
        except (TypeError, ValueError, Exception):
            pass

    raise ValueError('Invalid time format {}. Allowed formats are {}'.format(repr(time_string), repr(formats)))


def make_datetime(date_string, formats=None):
    """Make the datetime from the given date time string.

    Args:
        date_string (str): Datetime string '04:00 PM' ...
        formats (list): List of acceptable datetime string formats.

    Returns:
        dt (datetime.datetime): Datetime object or None.
    """
    if isinstance(date_string, datetime.datetime):
        return date_string

    if formats is None:
        formats = DATETIME_FORMATS

    for fmt in formats:
        try:
            return datetime.datetime.strptime(date_string, fmt)
        except (TypeError, ValueError, Exception):
            pass

    raise ValueError('Invalid datetime format {}. Allowed formats are {}'.format(repr(date_string), repr(formats)))


def str_date(dt: datetime.date) -> str:
    """Return the date as a string."""
    return dt.strftime(DATE_FORMATS[0])


def str_time(dt: datetime.time) -> str:
    """Return the time as a string"""
    return dt.strftime(TIME_FORMATS[0])


def str_datetime(dt: datetime.datetime) -> str:
    """Return the datetime as a string."""
    return dt.strftime(DATETIME_FORMATS[0])


# ========== Register Datetime compatibility ==========
def date_encode(obj):
    return {'value': str_date(obj)}


def date_decode(obj):
    return make_date(obj['value'])


def time_encode(obj):
    return {'value': str_time(obj)}


def time_decode(obj):
    return make_time(obj['value'])


def datetime_encode(obj):
    return {'value': str_datetime(obj)}


def datetime_decode(obj):
    return make_datetime(obj['value'])


register(datetime.date, date_encode, date_decode)
register(datetime.time, time_encode, time_decode)
register(datetime.datetime, datetime_encode, datetime_decode)


# ========= Properties ==========
def date_property(attr, allow_none=True, default=MISSING, default_factory=MISSING, formats: List[str] = None, **kwargs):
    """Create a date dataclass property where the underlying datetime is saved to "_attr".

    Args:
        attr (str): Attribute name (example: "created_on"
        allow_none (bool)[True]: Allows the property to be set to None. This is needed if the default is None.
        default (object)[MISSING]: Default value for the dataclass
        default_factory (function)[MISSING]: Function that returns the default value.
        formats (list)[None]: List of string formats to accept.

    Returns:
        property (field_property): Dataclass field property for a date.
    """
    attr = '_' + attr
    typeref = Union[datetime.date, str]
    if allow_none:
        typeref = Union[datetime.date, str, None]

    if default == MISSING and default_factory == MISSING and allow_none:
        default = None

    def fget(self):
        return getattr(self, attr)

    def fset(self, value: typeref):
        if value is None and not allow_none:
            raise TypeError('Invalid date value given!')
        elif value is not None:
            value = make_date(value, formats=formats)
        setattr(self, attr, value)

    return field_property(fget, fset, doc='date property {}'.format(attr),
                          default=default, default_factory=default_factory, **kwargs)


def time_property(attr, allow_none=True, default=MISSING, default_factory=MISSING, formats: List[str] = None, **kwargs):
    """Create a time dataclass property where the underlying datetime is saved to "_attr".

    Args:
        attr (str): Attribute name (example: "created_on"
        allow_none (bool)[True]: Allows the property to be set to None. This is needed if the default is None.
        default (object)[MISSING]: Default value for the dataclass
        default_factory (function)[MISSING]: Function that returns the default value.
        formats (list)[None]: List of string formats to accept.

    Returns:
        property (field_property): Dataclass field property for a time.
    """
    attr = '_' + attr
    typeref = Union[datetime.time, str]
    if allow_none:
        typeref = Union[datetime.time, str, None]

    if default == MISSING and default_factory == MISSING and allow_none:
        default = None

    def fget(self):
        return getattr(self, attr)

    def fset(self, value: typeref):
        if value is None and not allow_none:
            raise TypeError('Invalid time value given!')
        elif value is not None:
            value = make_time(value, formats=formats)
        setattr(self, attr, value)

    return field_property(fget, fset, doc='time property {}'.format(attr),
                          default=default, default_factory=default_factory, **kwargs)


def datetime_property(attr, allow_none=True, default=MISSING, default_factory=MISSING, formats: List[str] = None, **kwargs):
    """Create a datetime dataclass property where the underlying datetime is saved to "_attr".

    Args:
        attr (str): Attribute name (example: "created_on"
        allow_none (bool)[True]: Allows the property to be set to None. This is needed if the default is None.
        default (object)[MISSING]: Default value for the dataclass
        default_factory (function)[MISSING]: Function that returns the default value.
        formats (list)[None]: List of string formats to accept.

    Returns:
        property (field_property): Dataclass field property for a datetime.
    """
    attr = '_' + attr
    typeref = Union[datetime.datetime, str]
    if allow_none:
        typeref = Union[datetime.datetime, str, None]

    if default == MISSING and default_factory == MISSING and allow_none:
        default = None

    def fget(self):
        return getattr(self, attr)

    def fset(self, value: typeref):
        if value is None and not allow_none:
            raise TypeError('Invalid datetime value given!')
        elif value is not None:
            value = make_datetime(value, formats=formats)
        setattr(self, attr, value)

    return field_property(fget, fset, doc='datetime property {}'.format(attr),
                          default=default, default_factory=default_factory, **kwargs)


def timedelta_from_attrs(obj) -> datetime.timedelta:
    """Return a timedelta from attributes that exist in the given object.

    Attributes are 'weeks', 'days', 'hours', 'minutes', 'seconds', 'milliseconds', and 'microseconds'.

    Args:
        obj (object): Object with timedelta attributes.

    Returns:
        td (datetime.timedelta): Timedelta object.
    """
    weeks = getattr(obj, 'weeks', 0)
    days = getattr(obj, 'days', 0)
    hours = getattr(obj, 'hours', 0)
    minutes = getattr(obj, 'minutes', 0)
    seconds = getattr(obj, 'seconds', 0)
    milliseconds = getattr(obj, 'milliseconds', 0)
    microseconds = getattr(obj, 'microseconds', 0)

    return datetime.timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds,
                              milliseconds=milliseconds, microseconds=microseconds)


def timedelta_to_attrs(obj, td: datetime.timedelta):
    """Save the given timedelta as attributes in the given object. This function does not save attributes if they do
    not exist.

    Attributes are 'weeks', 'days', 'hours', 'minutes', 'seconds', 'milliseconds', and 'microseconds'.

    Args:
        obj (object): Object with timedelta attributes.
        td (datetime.timedelta): Timedelta to save the attributes from.
    """
    if td is None:  # Protect the default of None
        return
    elif not isinstance(td, datetime.timedelta):
        raise TypeError('Invalid timedelta given!')

    days = td.days
    seconds = td.seconds
    microseconds = td.microseconds

    weeks = int(days / 7)
    days = int(days - weeks)
    if hasattr(obj, 'weeks'):
        obj.weeks = weeks
    if hasattr(obj, 'days'):
        obj.days = days

    hours = int(seconds / 3600)
    minutes = int((seconds - (hours * 3600)) / 60)
    seconds = int(seconds - (minutes * 60))
    if hasattr(obj, 'hours'):
        obj.hours = hours
    if hasattr(obj, 'minutes'):
        obj.minutes = minutes
    if hasattr(obj, 'seconds'):
        obj.seconds = seconds

    milliseconds = int(microseconds / 1000)
    microseconds = int(microseconds - (milliseconds * 1000))
    if hasattr(obj, 'milliseconds'):
        obj.milliseconds = milliseconds
    if hasattr(obj, 'microseconds'):
        obj.microseconds = microseconds


def timedelta_attr_property(required=False, **kwargs):
    """Return a timedelta property that uses a classes attributes for
    'weeks', 'days', 'hours', 'minutes', 'seconds', 'milliseconds', and 'microseconds'.

    Example:

        .. code-block:: python

            @dataclass
            class MyClass:
                days: int = 0
                hours: int = 0
                minutes: int = 0
                seconds: int = 0
                milliseconds: int = 0

                interval: datetime.timedelta = timedelta_helper_property()

    Returns:
        property (field_property): Timedelta property that uses a classes underlying attributes.
    """
    return field_property(timedelta_from_attrs, timedelta_to_attrs,
                          doc='Interval from the set time values', required=required, **kwargs)


def seconds_property(attr='seconds'):
    """Property for a seconds attribute to turn floating points into milliseconds.

    Args:
        attr (str)['seconds']: Attribute name

    Returns:
        property (field_property): Property that when given a float will set seconds and milliseconds.
    """
    attr = '_' + attr

    def fget(self) -> int:
        return getattr(self, attr, 0)

    def fset(self, value: Union[int, float]):
        if isinstance(value, float):
            mill = int((value % 1) * 1000)
            if mill:
                self.milliseconds = mill

        setattr(self, attr, int(value))

    return field_property(fget, fset, doc='Seconds in time. If float also set milliseconds', default=0)
