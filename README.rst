========================
Serial JSON
========================

Easily add custom JSON serialization


Code Example
============

Defaults
--------

.. code-block:: python

    import serial_json as json
    import datetime

    value = b'Hello World!'  # Bytes are not supported by json normally
    assert json.loads(json.dumps(value)) == value

    dt = datetime.datetime.now()  # datetimes are not supported by json normally
    assert json.loads(json.dumps(dt)) == dt


Custom
------

Custom serialization using a classes __getstate__ and __setstate__ methods.

.. code-block:: python

    import serial_json as json

    @json.register
    class MyClass(object):
        def __init__(self, x=0, y=0):
            self.x = x
            self.y = y

        def __eq__(self, other):
            """Compare objects."""
            try:
                return self.x == other.x and self.y == other.y
            except (AttributeError, Exception):
                return False

        def __getstate__(self):
            return {'x': self.x, 'y': self.y}

        def __setstate__(self, state):
            self.x = state.get('x', 0)
            self.y = state.get('y', 0)

    my_value = MyClass()
    assert json.loads(json.dumps(my_value)) == my_value


Custom serialization with functions instead of a class with getstate and setstate.

.. code-block:: python

    import serial_json

    class MyClass(object):
        def __init__(self, x=0, y=0):
            self.x = x
            self.y = y

        def __eq__(self, other):
            """Compare objects."""
            try:
                return self.x == other.x and self.y == other.y
            except (AttributeError, Exception):
                return False

    def cls_to_dict(obj):
        return {'x': obj.x, 'y': obj.y}

    def cls_from_dict(obj):
        return MyClass(**obj)

    # Register the serialize and deserialize functions
    serial_json.register(MyClass, cls_to_dict, cls_from_dict)

    my_value = MyClass()
    assert serial_json.loads(serial_json.dumps(my_value)) == my_value

dataclass
---------

Dataclasses can be used through inheritance with `DataClass` or through the decorator `dataclass`.

.. code-block:: python

    import serial_json
    from serial_json import dataclass, field_property, field

    @dataclass
    class Point:
        x: int
        y: int
        z: int = field(default=0, skip_repr=0, skip_dict=0)  # Do not include in repr if value is 0

    help(Point)

    # p = Point()  # Raises error for required positional arguments
    p = Point(1, 2)
    assert p.x == 1
    assert p.y == 2
    assert p.z == 0

    class Location(serial_json.DataClass):
        name: str
        point: Point = Point(0, 0, 0)

        @field_property(default=Point(1, 1, 0))
        def point2(self):
            return self._point2

        @point2.setter
        def point2(self, value):
            if isinstance(value, (list, tuple)) and len(value) >= 2:
                value = Point(*value)
            elif isinstance(value, dict):
                value = Point(**value)

            if not isinstance(value, Point):
                raise TypeError('Given value must be a Point!')
            self._point2 = value

    help(Location)

    l = Location('hello')
    assert l.name == 'hello'
    assert l.point == Point(0, 0, 0)
    assert l.point2 == Point(1, 1, 0)

    l2 = Location('111', point=Point(x=1, y=1, z=1), point2=(2, 2, 0))
    assert l2.name == '111'
    assert l2.point == Point(1, 1, 1)
    assert l2.point2 == Point(2, 2, 0)
    assert str(l2) == 'Location(name=111, point=Point(x=1, y=1, z=1), point2=Point(x=2, y=2))'  # skip repr


datetime property
-----------------

Additional datetime, date, time, and weekdays properties are available

.. code-block:: python

    import datetime
    from serial_json import dataclass, datetime_property, Weekdays, weekdays_property, weekdays_attr_property

    @dataclass
    class Item:
        created_on: datetime.datetime = datetime_property('created_on', default_factory=datetime.datetime.now)
        weekdays: Weekdays = weekdays_property('weekdays', default=Weekdays())

        sunday = weekdays_attr_property('weekdays', 'sunday')
        monday = weekdays_attr_property('weekdays', 'monday')
        tuesday = weekdays_attr_property('weekdays', 'tuesday')
        wednesday = weekdays_attr_property('weekdays', 'wednesday')
        thursday = weekdays_attr_property('weekdays', 'thursday')
        friday = weekdays_attr_property('weekdays', 'friday')
        saturday = weekdays_attr_property('weekdays', 'saturday')

    it = Item(weekdays='monday')
    assert it.created_on is not None
    assert it.created_on >= datetime.datetime.today().replace(hour=0)
    assert 'monday' in it.weekdays
    assert 'sunday' not in it.weekdays
    assert it.monday
    assert not it.sunday

    it = Item(weekdays=[], friday=True)
    assert it.created_on is not None
    assert it.created_on >= datetime.datetime.today().replace(hour=0)
    assert 'friday' in it.weekdays
    assert 'sunday' not in it.weekdays
    assert it.friday
    assert not it.sunday

    it = Item(sunday=False)
    assert it.created_on is not None
    assert it.created_on >= datetime.datetime.today().replace(hour=0)
    assert 'friday' in it.weekdays, it.weekdays
    assert 'sunday' not in it.weekdays, it.weekdays
    assert it.friday
    assert not it.sunday
