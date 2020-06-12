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
