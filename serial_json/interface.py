import inspect
import json
import functools


__all__ = ['Serializer', 'register', 'unregister', 'get_serializer', 'RegisterMetaclass', 'Message',
           'dumps', 'dump', 'loads', 'load', 'default', 'object_hook']


def base_create_object(cls):
    """Primitive create object. This will work if parent class overrides __new__ with *args, **kwargs."""
    # Create the object without failing from __init__ args (if parent class overrides __new__ with *args, **kwargs)
    obj = cls.__new__(cls)

    # Try to initialize properly (may fail because of no args)
    try:
        obj.__init__()
    except (TypeError, Exception):
        pass

    return obj


# ========== Serializers ==========
SERIALIZERS = []  # Serializer
SERIALIZER_TYPE = 'SERIALIZER_TYPE'
SERIALIZER_OBJ = 'SERIALIZER_OBJ'


class Serializer(object):
    """Serializer that will try to use an objects "__getstate__" and "__setstate__" methods.

    Encode functions should take in an object and return a dictionary

    Decode functions should take in a dictionary and return a new object from that objects data.
    """
    def __init__(self, cls, encode=None, decode=None):
        self.cls = cls
        self.serializer_name = '{}.{}'.format(self.cls.__module__, self.cls.__name__)

        if encode is not None:
            self.encode = encode
        if decode is not None:
            self.decode = decode

    def encode(self, obj):
        return obj.__getstate__()

    def decode(self, obj):
        try:
            new_obj = self.cls()
        except Exception as err:
            try:
                new_obj = base_create_object(self.cls)
            except (ValueError, TypeError, Exception):
                raise err

        new_obj.__setstate__(obj)
        return new_obj


def register(cls_obj=None, encode=None, decode=None):
    """Register a serializer class.

    By default the serializer will use the class type "__getstate__" and "__setstate__" methods if an encode and decode
    method is not given.

    Args:
        cls_obj (class/type): Class/Type/object to register the serializer encode and decode methods with.
        encode (function): Function to convert an object of this type to a dictionary.
        decode (function): Function to convert a dictionary representing this type into an object.

    Returns:
        cls (class/type/function): Class/Type that was registered OR decorator function.
    """
    global SERIALIZERS

    # ===== As Decorator =====
    if cls_obj is None:
        def wrapper(cls):
            register(cls_obj=cls_obj, encode=encode, decode=decode)
            return cls
        return wrapper

    # ===== Register the class as a serializer =====
    try:
        if not inspect.isclass(cls_obj):
            cls_obj = cls_obj.__class__
    except (AttributeError, Exception):
        pass

    # Save the serializer class
    serializer = Serializer(cls=cls_obj, encode=encode, decode=decode)
    registered = False
    for i, ser in enumerate(SERIALIZERS):
        if ser.cls == cls_obj:
            SERIALIZERS[i] = serializer
            registered = True

    if not registered:
        SERIALIZERS.append(serializer)

    return cls_obj


def unregister(cls_obj):
    """Remove a registered serializer."""
    global SERIALIZERS
    try:
        if not inspect.isclass(cls_obj):
            cls_obj = cls_obj.__class__
    except (AttributeError, Exception):
        pass

    for i in range(len(SERIALIZERS)):
        ser = SERIALIZERS[i]
        if ser.cls == cls_obj:
            SERIALIZERS.pop(i)
            break


def get_serializer(cls_obj):
    """Return a serializer class for the given type."""
    global SERIALIZERS

    # ===== Serializer from class/type =====
    try:
        if not isinstance(cls_obj, str) and not inspect.isclass(cls_obj):
            cls_obj = cls_obj.__class__
    except (AttributeError, Exception):
        pass

    first_sub = None
    for ser in SERIALIZERS:
        try:
            # Check if given object is class or matching string serializer_name
            if ser.cls == cls_obj or ser.serializer_name == cls_obj:
                return ser
            elif first_sub is None and issubclass(cls_obj, ser.cls):
                first_sub = ser
        except (TypeError, ValueError, Exception):
            pass

    return first_sub


# ========== Default Message Object ==========
class RegisterMetaclass(type):
    """Metaclass that automatically registers subclasses """
    def __new__(mcs, name, bases, class_dict):
        cls = type.__new__(mcs, name, bases, class_dict)
        register(cls)
        return cls


class Message(metaclass=RegisterMetaclass):
    def __new__(cls, *args, **kwargs):
        """Create new object (This works with base_create_object)"""
        obj = super().__new__(cls)
        return obj

    def __init__(self, *args, **kwargs):
        super().__init__()
        if len(kwargs) > 0:
            self.update(kwargs)

    def as_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_') and not k[0].isupper()}

    def update(self, d):
        for k, v in d.items():
            setattr(self, k, v)

    @classmethod
    def from_dict(cls, d):
        obj = base_create_object(cls)
        obj.update(d)
        return obj

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __eq__(self, other):
        try:
            return self.__getstate__() == other.__getstate__()
        except:
            return False

    def __getstate__(self):
        return self.as_dict()

    def __setstate__(self, state):
        self.update(state)


# ========== JSON Parsers ==========
_default_encoder = json._default_encoder
_default_decoder = json._default_decoder


def default(obj):
    """Default function for how to serialize an object."""
    # Get serializer
    ser = get_serializer(obj)

    if ser is not None:
        # Get the state dictionary
        d = ser.encode(obj)
        if not isinstance(d, dict):
            d = {SERIALIZER_OBJ: d}
        d[SERIALIZER_TYPE] = ser.serializer_name
        return d

    return _default_encoder.default(obj)


def object_hook(obj):
    """Default function for how to deserialize an object."""
    if isinstance(obj, dict) and SERIALIZER_TYPE in obj:
        name = obj.pop(SERIALIZER_TYPE, None)
        obj = obj.pop(SERIALIZER_OBJ, obj)
        if name is not None:
            ser = get_serializer(name)
            if ser is not None:
                return ser.decode(obj)

    if _default_decoder.object_hook is not None:
        return _default_decoder.object_hook(obj)
    return obj


@functools.wraps(json.dumps)
def dumps(obj, **kwargs):
    kwargs['default'] = default
    return json.dumps(obj, **kwargs)


@functools.wraps(json.dump)
def dump(obj, fp, **kwargs):
    kwargs['default'] = default
    return json.dump(obj, fp, **kwargs)


@functools.wraps(json.loads)
def loads(s, **kwargs):
    kwargs['object_hook'] = object_hook
    return json.loads(s, **kwargs)


@functools.wraps(json.load)
def load(fp, **kwargs):
    kwargs['object_hook'] = object_hook
    return json.load(fp, **kwargs)
