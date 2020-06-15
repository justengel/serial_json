

def test_date():
    import datetime
    import serial_json
    import serial_json.datetime_support   # Not needed in normal use

    d = datetime.date(year=2020, month=1, day=3)
    # assert serial_json.dumps(d) == '{"value": "2020-01-03", "SERIALIZER_TYPE": "datetime.date"}'
    assert serial_json.loads(serial_json.dumps(d)) == d


def test_time():
    import datetime
    import serial_json
    import serial_json.datetime_support   # Not needed in normal use

    d = datetime.time(hour=1, minute=40, second=50)
    assert serial_json.loads(serial_json.dumps(d)) == d


def test_datetime():
    import datetime
    import serial_json
    import serial_json.datetime_support   # Not needed in normal use

    d = datetime.datetime(year=2020, month=1, day=3, hour=1, minute=40, second=50)
    assert serial_json.loads(serial_json.dumps(d)) == d


def test_dataclass_datetime_property():
    import time
    import datetime
    from serial_json import dataclass, datetime_property

    @dataclass
    class Record:
        name: str
        created_on: datetime.datetime = datetime_property('created_on', default_factory=datetime.datetime.now)

    before = datetime.datetime.now()
    time.sleep(1)
    rec = Record('Hello')
    assert rec.name == 'Hello'
    assert rec.created_on is not None
    assert rec.created_on > before


if __name__ == '__main__':
    test_date()
    test_time()
    test_datetime()
    test_dataclass_datetime_property()

    print('All tests finished successfully!')
