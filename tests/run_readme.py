

def run_readme_custom_class():
    import serial_json

    @serial_json.register  # Register this class using __getstate__ and __setstate__ by default
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
    assert serial_json.loads(serial_json.dumps(my_value)) == my_value


def run_readme_custom_funcs():
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


if __name__ == '__main__':
    run_readme_custom_class()
    run_readme_custom_funcs()

    print('Finished successfully!')
