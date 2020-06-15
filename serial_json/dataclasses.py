# https://developers.google.com/calendar/create-events
import copy
from inspect import signature, Signature, Parameter
from typing import Any, Callable
from collections import OrderedDict

from .interface import register, dumps, loads


__all__ = ['MISSING', 'field', 'field_property', 'DataclassMeta', 'DataClass', 'dataclass', 'Message']


class MISSING(object):
    pass


class field(object):
    """Dataclass field attribute

    Args:
        default (object/Any): Default value on init.
        default_factory (function/Callable): Function that returns the default value.
        required (bool)[None]: If None required if init and no defaults.
            This makes the __init__ require a positional, keyword, or default value.
        repr (bool)[True]: Include this field in the repr.
        hash (bool)[None]: If True include in __hash__. If None include in __hash__ if compare is True.
        init (bool)[True]: Include this field in the __init__. If False set the value from the default value.
        compare (bool)[True]: Include this field in the __eq__ comparison.
        metadata (dict)[None]: Unused.
        dict (bool)[True]: Include this field in the dict() method.
        skip_dict (object/Any)[MISSING]: Do not include this field in the dict() if the set value equals this value.
        skip_repr (object/Any)[MISSING]: Do not include this field in the __repr__ if the set value equals this value.
        name (str)[MISSING]: Field variable name. This is automatically set.
        type (object/type): Field type. Used in __init__ doc string and annotation.
    """
    def __init__(self, default=MISSING, default_factory=MISSING, required=None, repr=True, hash=None, init=True,
                 compare=True, metadata=None, dict=True, skip_dict=MISSING, skip_repr=MISSING, name=MISSING, type=Any,
                 doc='', **kwargs):
        super().__init__()
        self.__doc__ = doc

        self.default = default
        self.default_factory = default_factory
        self.required = required
        self.repr = repr
        self.skip_repr = skip_repr
        self.hash = hash
        self.init = init
        self.compare = compare
        self.metadata = metadata
        self.dict = dict
        self.skip_dict = skip_dict
        self.type = type
        self.name = name

        if self.required is None:
            self.required = not self.has_default()

        # Save other given attributes
        for k, v in kwargs.items():
            setattr(self, k, v)

    def set_name(self, n, replace=True):
        """Set the name."""
        if self.name == MISSING or replace:
            self.name = n

    def is_required(self):
        """Return if this field is required to be set in the init with a positional, keyword, or default value."""
        return self.init and self.required

    def is_positional(self):
        """Return if this argument is required in init."""
        return self.is_required() and not self.has_default()

    def has_default(self):
        """Return if this field has a default."""
        return self.default != MISSING or self.default_factory != MISSING

    def set_default(self, default):
        """Set the default value."""
        self.default = default
        return self

    def set_default_factory(self, default_factory):
        """Set the default factory function to get the default value."""
        self.default_factory = default_factory
        return self

    def get_default_value(self, obj=None):
        """Return this object's field default value.

        Args:
            obj (object)[None]: Instance object for this field.

        Raises:
            error (TypeError): If a default is not set and this argument is required.

        Returns:
            value (object/Any): Default Value.
        """
        if self.default != MISSING:
            try:
                return copy.copy(self.default)
            except (TypeError, ValueError, Exception):
                pass
            return self.default
        elif self.default_factory != MISSING:
            try:
                return self.default_factory.__get__(obj, type(obj))()
            except (TypeError, ValueError, Exception):
                pass
            return self.default_factory()
        raise TypeError('missing required argument: {}'.format(self.name))

    def get_default_str(self):
        """Return this fields default value for the doc string."""
        if self.default != MISSING:
            try:
                return copy.copy(self.default)
            except (TypeError, ValueError, Exception):
                pass
            return self.default
        elif self.default_factory != MISSING:
            return str(self.default_factory)
        return None

    def get_type(self):
        """Return this field's type as a string name."""
        typ = Any
        if self.type is not None:
            typ = self.type
        elif self.default != MISSING:
            typ = type(self.default)
        elif self.default_factory != MISSING:
            try:
                typ = type(self.default_factory())
            except (TypeError, ValueError, AttributeError, Exception):
                pass

        return typ

    def get_type_str(self):
        typ = self.get_type()
        try:
            return typ.__name__
        except (AttributeError, Exception):
            return typ

    def as_parameter(self):
        default = Parameter.empty
        annotation = self.get_type()
        if self.is_positional():
            kind = Parameter.POSITIONAL_ONLY
        elif self.has_default():
            kind = Parameter.POSITIONAL_OR_KEYWORD
            default = self.get_default_str()
        else:
            kind = Parameter.VAR_KEYWORD

        return Parameter(name=self.name, kind=kind, default=default, annotation=annotation)


class field_property(field):
    """Field that works as a property."""
    def __init__(self, fget=None, fset=None, fdel=None, doc='',
                 default=MISSING, default_factory=MISSING, required=False, repr=True, hash=None, init=True,
                 compare=True, metadata=None, dict=True, skip_dict=MISSING, skip_repr=MISSING, name=MISSING, type=None,
                 **kwargs):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        super().__init__(default=default, default_factory=default_factory, required=required, repr=repr, hash=hash,
                         init=init, compare=compare, metadata=metadata, dict=dict, skip_dict=skip_dict,
                         skip_repr=skip_repr, name=name, type=type, doc=doc, **kwargs)

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self, fget: Callable[[Any], Any]) -> 'field_property':
        self.fget = fget
        return self

    __call__ = getter

    def setter(self, fset: Callable[[Any, Any], None]) -> 'field_property':
        self.fset = fset
        return self

    def deleter(self, fdel: Callable[[Any], None]) -> 'field_property':
        self.fdel = fdel
        return self


class DataclassMeta(type):
    def __new__(cls, name, bases, dct):
        new_cls = super().__new__(cls, name, bases, dct)
        return cls.dataclass(new_cls)

    @classmethod
    def dataclass(cls, new_cls=None, init=True, repr=True, eq=True, order=False, unsafe_hash=False, dict=True,
                       frozen=False, **kwargs):
        """Return the given class as a dataclass."""
        if new_cls is None:
            def decorator(new_cls):
                return cls.dataclass(new_cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash,
                                          dict=dict, frozen=frozen, **kwargs)
            return decorator

        cls.make_fields(new_cls)

        if init and new_cls.__init__ == object.__init__ and not getattr(new_cls.__init__, '__is_dataclass__', False):
            # Set the __init__ function
            def __init__(self, *args, **kwargs):
                return cls.init_func(self, *args, **kwargs)
            __init__.__is_dataclass__ = True
            new_cls.__init__ = __init__

        if init and getattr(new_cls.__init__, '__is_dataclass__', False):
            # Make the signature and doc string for the __init__ function
            try:
                new_cls.__init__.__signature__ = cls.make_init_signature(new_cls)
                doc = cls.make_init_docs(new_cls)
                if not new_cls.__doc__:
                    new_cls.__doc__ = doc
                new_cls.__init__.__doc__ = doc
            except AttributeError:
                pass

        if dict:
            if 'dict' not in new_cls.__dict__:
                new_cls.dict = cls.asdict
            if not hasattr(new_cls, '__getstate__'):
                new_cls.__getstate__ = cls.getstate_func
            if not hasattr(new_cls, '__setstate__'):
                new_cls.__setstate__ = cls.setstate_func
            if not hasattr(new_cls, 'json'):
                new_cls.json = cls.json
            if not hasattr(new_cls, 'from_json'):
                new_cls.from_json = cls.from_json

        if new_cls.__hash__ == object.__hash__:
            new_cls.__hash__ = cls.hash_func

        if eq and new_cls.__eq__ == object.__eq__:
            new_cls.__eq__ = cls.compare_func

        if repr and new_cls.__repr__ == object.__repr__:
            new_cls.__repr__ = cls.repr_func

        new_cls.__is_frozen__ = frozen

        # Register for serialization
        register(new_cls)

        return new_cls

    @staticmethod
    def make_fields(cls):
        bases = cls.__bases__

        # Setup annotations and fields
        if not hasattr(cls, '__annotations__'):
            cls.__annotations__ = OrderedDict()

        if not hasattr(cls, '__fields__'):
            cls.__fields__ = OrderedDict()
        elif any(getattr(base, '__fields__', {}) is cls.__fields__ for base in bases):
            cls.__fields__ = cls.__fields__.copy()

        if not hasattr(cls, '__dataclass_properties__'):
            cls.__dataclass_properties__ = {'allow_extra_init': True}
        elif any(getattr(base, '__dataclass_properties__', {}) is cls.__dataclass_properties__ for base in bases):
            cls.__dataclass_properties__ = cls.__dataclass_properties__.copy()

        # Make annotations
        for name, attr in cls.__dict__.items():
            if name.startswith('__'):
                continue

            if name in cls.__fields__ and name not in cls.__annotations__:
                cls.__annotations__[name] = cls.__fields__[name].get_type()
            elif isinstance(attr, field) and name not in cls.__annotations__:
                cls.__annotations__[name] = attr.get_type()
            elif isinstance(attr, property) and name not in cls.__annotations__:
                ret_typ = signature(attr.fget).return_annotation
                if ret_typ == Signature.empty:
                    ret_typ = Any
                cls.__annotations__[name] = ret_typ

        # Make fields
        for name, typ in cls.__annotations__.items():
            if name not in cls.__fields__:
                f = cls.__dict__.get(name, MISSING)
                if not isinstance(f, field):
                    if f != MISSING:
                        f = cls.__fields__.get(name, field(default=f, type=typ))
                    else:
                        f = cls.__fields__.get(name, field(default=MISSING, type=typ))
                else:
                    f.type = typ
                cls.__fields__[name] = f
                f.set_name(name, replace=False)

    @staticmethod
    def make_init_docs(cls):
        def args():
            for f in cls.__fields__.values():
                if f.init:
                    if f.is_positional():
                        yield '{name} ({type}): {name} value\n'.format(
                                name=f.name, type=f.get_type_str(), default=f.get_default_str())
                    elif f.has_default():
                        yield '{name} ({type})[{default}]: {name} value\n'.format(
                                name=f.name, type=f.get_type_str(), default=f.get_default_str())

        return "\n" \
               "    Data object {}.\n" \
               "\n" \
               "    Args:\n" \
               "        {}\n".format(cls.__name__, '        '.join(args()))

    @staticmethod
    def make_init_signature(cls):
        self_param = Parameter(name='self', kind=Parameter.POSITIONAL_ONLY)  # First param must be self
        params = [self_param] + [f.as_parameter() for f in cls.__fields__.values()]
        params = sorted(params, key=lambda p: p.kind)
        return Signature(parameters=params)

    # @classmethod
    # def make_init(cls, new_cls):
    #     def args():
    #         for f in new_cls.__fields__.values():
    #             if f.init:
    #                 if f.is_positional():
    #                     yield '{name}: {type}'.format(name=f.name, type=f.get_type_str())
    #                 elif f.has_default():
    #                     yield '{name}: {type} = MISSING'.format(name=f.name, type=f.get_type_str())
    #
    #     def init_kwargs():
    #         for f in new_cls.__fields__.values():
    #             if f.init:
    #                 yield '{name}={name}'.format(name=f.name)
    #
    #     txt = '\n'.join(('def __init__(self, {}, **kwargs):'.format(', '.join(args())),
    #                      '    """{}"""'.format(cls.make_init_docs(new_cls)),
    #                      '    dataclass_cls.init_func(self, {}, **kwargs)'.format(', '.join(init_kwargs())),
    #                      '    ',
    #                      '    if hasattr(self, "__post_init__"):',
    #                      '        self.__post_init__()', ''))
    #
    #     if new_cls.__module__ in sys.modules:
    #         glbls = sys.modules[new_cls.__module__].__dict__
    #     else:
    #         glbls = {}
    #
    #     ns = {}
    #     glbls['dataclass_cls'] = DataclassMeta
    #     glbls['MISSING'] = MISSING
    #     exec(txt, glbls, ns)
    #     init = ns['__init__']
    #     init.__is_dataclass__ = True
    #     return init

    @staticmethod
    def init_func(self, *args, **kwargs):
        # Set positional arguments
        len_args = len(args)
        for i, f in enumerate(self.__fields__.values()):
            if f.init and i < len_args and args[i] != MISSING:  # Positional arguments are prioritized
                setattr(self, f.name, args[i])
            elif f.init and f.name in kwargs:
                if kwargs[f.name] == MISSING:
                    kwargs[f.name] = f.get_default_value(self)
                setattr(self, f.name, kwargs.pop(f.name))
            elif f.has_default():  # If no default the field is not set on init
                setattr(self, f.name, f.get_default_value(self))
            elif f.is_required():
                raise TypeError('missing required argument {}'.format(f.name))

        # Check left over keyword arguments:
        if not self.__dataclass_properties__.get('allow_extra_init', True) and len(kwargs) > 0:
            raise TypeError("__init__() got unexpected keyword argument '{}'".format(list(kwargs)[0]))

        # Run post init function
        post_init = getattr(self, '__post_init__', None)
        if callable(post_init):
            post_init()

        # Freeze the object from changing
        if getattr(self, '__is_frozen__', False):
            def setter_func(self, name, value):
                raise TypeError('Cannot set attr on frozen object!')
            self.__setattr__ = setter_func.__get__(self, type(self))

    @staticmethod
    def asdict(self):
        return {f.name: getattr(self, f.name, MISSING) for f in self.__fields__.values()
                if f.dict and f.skip_dict != getattr(self, f.name, MISSING)}

    @staticmethod
    def hash_func(self):
        tup = tuple('{}={}'.format(f.name, getattr(self, f.name, MISSING)) for f in self.__fields__.values()
                    if f.hash or (f.hash is None and f.compare))
        return hash(tup)

    @staticmethod
    def compare_func(self, other):
        if not hasattr(other, '__fields__'):
            return False
        me = {f.name: getattr(self, f.name, MISSING) for f in self.__fields__.values() if f.compare}
        other = {f.name: getattr(other, f.name, MISSING) for f in other.__fields__.values() if f.compare}
        return me == other

    @staticmethod
    def repr_func(self):
        args = ['{}={}'.format(f.name, getattr(self, f.name, 'MISSING'))
                for f in self.__fields__.values()
                if f.repr and f.skip_repr != getattr(self, f.name, MISSING)]
        return '{}({})'.format(self.__class__.__name__, ', '.join(args))

    @staticmethod
    def getstate_func(self):
        return self.dict()

    @staticmethod
    def setstate_func(self, state):
        # Copy may improperly set a default skip_dict values to the field object and not the default.
        # The set defaults below fixes issue with copy.copy on field(skip_dict=default_value)
        for f in self.__fields__.values():
            if f.has_default():
                # Only set fields that have a default
                setattr(self, f.name, f.get_default_value(self))

        # Set the given state values
        for k, v in state.items():
            setattr(self, k, v)

    @staticmethod
    def json(self):
        return dumps(self)

    @staticmethod
    def from_json(text):
        if isinstance(text, bytes):
            text = text.decode()
        return loads(text)


class DataClass(metaclass=DataclassMeta):
    def __init__(self, *args, **kwargs):  # Defined for IDE argument highlighting
        DataclassMeta.init_func(self, *args, **kwargs)

    __init__.__is_dataclass__ = True


dataclass = DataclassMeta.dataclass


class Message(DataClass):
    pass
