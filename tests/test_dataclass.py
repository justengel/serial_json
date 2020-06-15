

def test_dataclass_func():
    from serial_json.dataclasses import dataclass

    @dataclass
    class MyClass:
        x: int
        y: int
        z: int = 1

    try:
        m = MyClass()
        raise AssertionError('Positional argument required!')
    except TypeError:
        pass

    try:
        m = MyClass(1)
        raise AssertionError('Positional argument required!')
    except TypeError:
        pass

    m = MyClass(1, 2)
    assert m.x == 1
    assert m.y == 2
    assert m.z == 1
    assert repr(m) == 'MyClass(x=1, y=2, z=1)'


def test_dataclass_property():
    from serial_json.dataclasses import dataclass

    @dataclass
    class MyClass:
        x: int
        y: int
        z: int = 1

        @property
        def w(self) -> int:
            return self._w

        @w.setter
        def w(self, value):
            self._w = value

    try:
        m = MyClass()
        raise AssertionError('Positional argument required!')
    except TypeError:
        pass

    try:
        m = MyClass(1)
        raise AssertionError('Positional argument required!')
    except TypeError:
        pass

    m = MyClass(1, 2, w=2)
    assert m.x == 1
    assert m.y == 2
    assert m.z == 1
    assert m.w == 2


def test_dataclass_field_property():
    from serial_json.dataclasses import dataclass, field_property

    @dataclass
    class MyClass:
        x: int
        y: int
        z: int = 1

        @field_property(default=0)
        def w(self) -> int:
            return self._w

        @w.setter
        def w(self, value):
            self._w = value

    try:
        m = MyClass()
        raise AssertionError('Positional argument required!')
    except TypeError:
        pass

    try:
        m = MyClass(1)
        raise AssertionError('Positional argument required!')
    except TypeError:
        pass

    m = MyClass(1, 2)
    assert m.x == 1
    assert m.y == 2
    assert m.z == 1
    assert m.w == 0


def test_dataclass_inheritance():
    from serial_json.dataclasses import dataclass, field_property

    @dataclass
    class MyClass:
        x: int
        y: int

        @field_property(default=0)
        def z(self) -> int:
            return self._z

        @z.setter
        def z(self, value):
            self._z = value

    @dataclass
    class MyClass2(MyClass):
        w: int = 1

    try:
        m = MyClass2()
        raise AssertionError('Positional argument required!')
    except TypeError:
        pass

    try:
        m = MyClass2(1)
        raise AssertionError('Positional argument required!')
    except TypeError:
        pass

    m = MyClass2(1, 2)
    assert m.x == 1
    assert m.y == 2
    assert m.z == 0
    assert m.w == 1

    m = MyClass2(1, 2, z=3, w=4)
    assert m.x == 1
    assert m.y == 2
    assert m.z == 3
    assert m.w == 4


def test_dataclass_class():
    from serial_json.dataclasses import DataClass, field_property

    class MyClass(DataClass):
        x: int
        y: int

        @field_property(default=0)
        def z(self) -> int:
            return self._z

        @z.setter
        def z(self, value):
            self._z = value

    class MyClass2(MyClass):
        w: int = 1

    try:
        m = MyClass2()
        raise AssertionError('Positional argument required!')
    except TypeError:
        pass

    try:
        m = MyClass2(1)
        raise AssertionError('Positional argument required!')
    except TypeError:
        pass

    m = MyClass2(1, 2)
    assert m.x == 1
    assert m.y == 2
    assert m.z == 0
    assert m.w == 1

    m = MyClass2(1, 2, z=3, w=4)
    assert m.x == 1
    assert m.y == 2
    assert m.z == 3
    assert m.w == 4


def test_dataclass_do_not_replace():
    from serial_json.dataclasses import dataclass, field_property

    @dataclass
    class MyClass:
        x: int
        y: int

        def __init__(self, x=42, y=43):
            self.x = x
            self.y = y

    m = MyClass()
    assert m.x == 42
    assert m.y == 43

    try:
        m = MyClass(1, 2, z=3)
        raise AssertionError('dataclass improperly overrides __init__')
    except TypeError:
        pass  # This should hit here

    # ===== Check to keep parent __init__ =====
    @dataclass
    class MyClass2(MyClass):
        x: int
        y: int
        z: int = 1

    m = MyClass2()
    assert m.x == 42
    assert m.y == 43

    try:
        m = MyClass2(1, 2, z=3)
        raise AssertionError('dataclass improperly overrides __init__')
    except TypeError:
        pass  # This should hit here

    # ===== Check dataclass init argument ======
    @dataclass(init=False)
    class MyClass:
        x: int
        y: int

    m = MyClass()
    assert not hasattr(m, 'x')
    assert not hasattr(m, 'y')
    assert repr(m) == 'MyClass()'  # Ignore MISSING with skip_repr == MISSING

    try:
        m = MyClass(1, 2)
        raise AssertionError('dataclass improperly overrides __init__')
    except TypeError:
        pass  # This should hit here


def test_dataclass_serial_json():
    from serial_json import dumps, loads, dataclass, field_property

    @dataclass
    class MyClass:
        x: int
        y: int

        @field_property(default=1)
        def z(self):
            return self._z

        @z.setter
        def z(self, value):
            self._z = value

    m = MyClass(0, 0)
    text = dumps(m)
    assert text == '{"x": 0, "y": 0, "z": 1, "SERIALIZER_TYPE": "test_dataclass_serial_json.<locals>.MyClass"}', text

    loaded = loads(text)
    assert loaded == m
    assert loaded.x == m.x
    assert loaded.y == m.y
    assert loaded.z == m.z


def test_dataclass_nested():
    from serial_json import dumps, loads, dataclass, field_property

    @dataclass
    class Point:
        x: int
        y: int

        @field_property(default=1)
        def z(self):
            return self._z

        @z.setter
        def z(self, value):
            self._z = value

    @dataclass
    class Location:
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

    m2 = Location('hello')
    assert m2.name == 'hello'
    assert m2.point.x == 0
    assert m2.point.y == 0
    assert m2.point.z == 0

    assert m2.point2 == Point(1, 1, 0)
    assert m2.point2.x == 1
    assert m2.point2.y == 1
    assert m2.point2.z == 0

    m2.point.x = 1
    m2.point.y = 1
    m2.point.z = 1
    assert m2.point.x == 1
    assert m2.point.y == 1
    assert m2.point.z == 1

    # Check that class default did not change
    assert m2.point != Location.point
    assert m2.point.x != Location.point.x
    assert m2.point.y != Location.point.y
    assert m2.point.z != Location.point.z

    text = dumps(m2)
    assert text == '{"name": "hello", "point": {"x": 1, "y": 1, "z": 1, ' \
                   '"SERIALIZER_TYPE": "test_dataclass_nested.<locals>.Point"}, "point2": {"x": 1, "y": 1, "z": 0, ' \
                   '"SERIALIZER_TYPE": "test_dataclass_nested.<locals>.Point"}, ' \
                   '"SERIALIZER_TYPE": "test_dataclass_nested.<locals>.Location"}', text

    loaded = loads(text)
    assert loaded == m2
    assert loaded.name == m2.name
    assert loaded.point == m2.point
    assert loaded.point.x == m2.point.x
    assert loaded.point.y == m2.point.y
    assert loaded.point.z == m2.point.z


if __name__ == '__main__':
    test_dataclass_func()
    test_dataclass_property()
    test_dataclass_field_property()
    test_dataclass_inheritance()
    test_dataclass_class()
    test_dataclass_do_not_replace()
    test_dataclass_serial_json()
    test_dataclass_nested()

    print('All tests finished successfully!')
