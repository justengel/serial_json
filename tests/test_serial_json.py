
def test_Message():
    import serial_json

    class Item(serial_json.Message):  # Base classes of Message are automatically registered
        def __init__(self, name, value):
            super().__init__()
            self.name = name
            self.value = value

    item = Item('abc', 123)
    item2 = serial_json.loads(serial_json.dumps(item))
    assert item == item2
    assert item.name == item2.name
    assert item.value == item2.value

    # Test additional messages with only using kwargs to set attrs
    class NewItem(serial_json.Message):  # Base classes of Message are automatically registered
        def __init__(self, name2, value2):
            super().__init__(name2=name2, value2=value2)

    new_item = NewItem('abc', 123)
    new_item2 = serial_json.loads(serial_json.dumps(new_item))
    assert new_item != item
    assert new_item2 != item2
    assert new_item == new_item2
    assert new_item['name2'] == new_item2.name2
    assert new_item.value2 == new_item2.value2


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
    test_Message()
    test_bytes()
    test_date()
    test_time()
    test_datetime()

    print('All tests finished successfully!')
