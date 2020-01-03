import datetime
from serial_json.interface import register


__all__ = ['TIME_FORMATS', 'DATE_FORMATS', 'DATETIME_FORMATS', 'make_time', 'make_date', 'make_datetime']


TIME_FORMATS = [
    '%I:%M:%S %p',     # '02:24:55 PM'
    '%I:%M:%S.%f %p',  # '02:24:55.000200 PM'
    '%I:%M %p',        # '02:24 PM'
    '%H:%M:%S',        # '14:24:55'
    '%H:%M:%S.%f',     # '14:24:55.000200'
    '%H:%M',           # '14:24'
    ]

DATE_FORMATS = [
    '%Y-%m-%d', '%m/%d/%Y',   # '2019-04-17', '04/17/2019'
    '%b %d %Y', '%b %d, %Y',  # 'Apr 17 2019', 'Apr 17, 2019'
    '%d %b %Y', '%d %b, %Y',  # '17 Apr 2019', '17 Apr, 2019'
    '%B %d %Y', '%B %d, %Y',  # 'April 17 2019', 'April 17, 2019'
    '%d %B %Y', '%d %B, %Y',  # '17 April 2019', '17 April, 2019'
    ]

DATETIME_FORMATS = [d + ' ' + t for t in TIME_FORMATS for d in DATE_FORMATS] + DATE_FORMATS + TIME_FORMATS


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

    raise ValueError('Invalid date format {}. Allowed formats are {}'.format(repr(date_string), repr(formats)))


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


# ========== Register Datetime compatibility ==========
def date_encode(obj):
    return {'value': obj.strftime(DATE_FORMATS[0])}


def date_decode(obj):
    return make_date(obj['value'])


def time_encode(obj):
    return {'value': obj.strftime(TIME_FORMATS[0])}


def time_decode(obj):
    return make_time(obj['value'])


def datetime_encode(obj):
    return {'value': obj.strftime(DATETIME_FORMATS[0])}


def datetime_decode(obj):
    return make_datetime(obj['value'])


register(datetime.date, date_encode, date_decode)
register(datetime.time, time_encode, time_decode)
register(datetime.datetime, datetime_encode, datetime_decode)
