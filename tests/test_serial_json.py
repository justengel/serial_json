
def test_bytes():
    import serial_json as json

    bts = b'12345'
    assert json.loads(json.dumps(bts)) == bts


def test_date():
    import datetime
    import serial_json as json

    d = datetime.date(year=2020, month=1, day=3)
    # assert serial_json.dumps(d) == '{"value": "2020-01-03", "SERIALIZER_TYPE": "datetime.date"}'
    assert json.loads(json.dumps(d)) == d


def test_time():
    import datetime
    import serial_json as json

    d = datetime.time(hour=1, minute=40, second=50)
    assert json.loads(json.dumps(d)) == d


def test_datetime():
    import datetime
    import serial_json as json

    d = datetime.datetime(year=2020, month=1, day=3, hour=1, minute=40, second=50)
    assert json.loads(json.dumps(d)) == d


if __name__ == '__main__':
    test_bytes()
    test_date()
    test_time()
    test_datetime()

    print('All tests finished successfully!')
