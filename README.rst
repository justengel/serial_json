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
