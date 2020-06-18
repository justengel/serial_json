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
    def __new__(mcs, name, bases, dct):

        mcs.make_fields(name, bases, dct)
        mcs.make_funcs(name, bases, dct)

        new_cls = super().__new__(mcs, name, bases, dct)

        # Register for serialization
        register(new_cls)

        return new_cls

    @classmethod
    def dataclass(mcs, new_cls=None, init=True, repr=True, eq=True, order=False, unsafe_hash=False, dict=True,
                  frozen=False, **kwargs):
        """Return the given class as a dataclass."""
        if new_cls is None:
            def decorator(new_cls):
                return mcs.dataclass(new_cls, init=init, repr=repr, eq=eq, order=order, unsafe_hash=unsafe_hash,
                                     dict=dict, frozen=frozen, **kwargs)
            return decorator

        dct = mcs.make_fields(new_cls.__name__, new_cls.__bases__, OrderedDict(new_cls.__dict__))
        mcs.make_funcs(new_cls.__name__, new_cls.__bases__, dct, init=init, repr=repr, eq=eq, order=order,
                       unsafe_hash=unsafe_hash, dict=dict, frozen=frozen, **kwargs)

        # Update the classes values
        for k, v in dct.items():
            if k not in new_cls.__dict__ or v != new_cls.__dict__[k]:
                setattr(new_cls, k, v)
        # new_cls.__dict__.update(dct)  # Cannot modify mappingproxy

        # Register for serialization
        register(new_cls)

        return new_cls

    @staticmethod
    def make_fields(name, bases, dct, **kwargs):
        nd = {}
        if bases is not None:
            for base in reversed(bases):
                nd.update(base.__dict__)
        else:
            bases = tuple()
        nd.update(dct)

        # Setup annotations and fields
        annotate = nd.get('__annotations__', None)
        if annotate is None:
            dct['__annotations__'] = annotate = OrderedDict()

        fields = nd.get('__fields__', None)
        if fields is None:
            dct['__fields__'] = fields = OrderedDict()
        elif any(getattr(base, '__fields__', {}) is fields for base in bases):
            dct['__fields__'] = fields = fields.copy()

        dc_prop = nd.get('__dataclass_properties__', None)
        if dc_prop is None:
            dct['__dataclass_properties__'] = dc_prop = {'allow_extra_init': True}
        elif any(getattr(base, '__dataclass_properties__', {}) is dc_prop for base in bases):
            dct['__dataclass_properties__'] = dc_prop = dc_prop.copy()

        # Make annotations
        for name, attr in nd.items():
            if name.startswith('__'):
                continue

            if name in fields and name not in annotate:
                annotate[name] = fields[name].get_type()
            elif isinstance(attr, field) and name not in annotate:
                annotate[name] = attr.get_type()
            elif isinstance(attr, property) and name not in annotate:
                ret_typ = signature(attr.fget).return_annotation
                if ret_typ == Signature.empty:
                    ret_typ = Any
                annotate[name] = ret_typ

        # Make fields
        for name, typ in annotate.items():
            if name not in fields:
                f = nd.get(name, MISSING)
                if not isinstance(f, field):
                    if f != MISSING:
                        f = fields.get(name, field(default=f, type=typ))
                    else:
                        f = fields.get(name, field(default=MISSING, type=typ))
                else:
                    f.type = typ
                fields[name] = f
                f.set_name(name, replace=False)

        return dct

    @classmethod
    def make_funcs(mcs, name, bases, dct, init=True, repr=True, eq=True, order=False, unsafe_hash=False, dict=True,
                   frozen=False, **kwargs):
        nd = {}
        if bases is not None:
            for base in reversed(bases):
                nd.update(base.__dict__)
        else:
            bases = tuple()
        nd.update(dct)

        init_func = nd.get('__init__', object.__init__)
        if init and init_func == object.__init__ and not getattr(init_func, '__is_dataclass__', False):
            # Set the __init__ function
            def __init__(self, *args, **kwargs):
                return mcs.init_func(self, *args, **kwargs)
            __init__.__is_dataclass__ = True
            dct['__init__'] = init_func = __init__

        if init and getattr(init_func, '__is_dataclass__', False):
            # Make the signature and doc string for the __init__ function
            try:
                fields = nd.get('__fields__', {})
                init_func.__signature__ = mcs.make_init_signature(fields)
                doc = mcs.make_init_docs(name, fields)
                if not nd.get('__doc__', ''):
                    dct['__doc__'] = doc
                init_func.__doc__ = doc
            except (KeyError, AttributeError):
                pass

        if dict:
            if 'dict' not in nd:
                dct['dict'] = mcs.asdict
            if '__getstate__' not in nd:
                dct['__getstate__'] = mcs.getstate_func
            if '__setstate__' not in nd:
                dct['__setstate__'] = mcs.setstate_func
            if 'json' not in nd:
                dct['json'] = mcs.json_func
            if 'from_json' not in nd:
                dct['from_json'] = mcs.from_json_func

        if nd.get('__hash__', object.__hash__) == object.__hash__:
            dct['__hash__'] = mcs.hash_func

        if eq and nd.get('__eq__', object.__eq__) == object.__eq__:
            dct['__eq__'] = mcs.compare_func

        if repr and nd.get('__repr__', object.__repr__) == object.__repr__:
            dct['__repr__'] = mcs.repr_func

        dct['__is_frozen__'] = frozen

        return dct

    @staticmethod
    def make_init_docs(name, fields):
        def args():
            for f in fields.values():
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
               "        {}\n".format(name, '        '.join(args()))

    @staticmethod
    def make_init_signature(fields):
        self_param = Parameter(name='self', kind=Parameter.POSITIONAL_ONLY)  # First param must be self
        params = [self_param] + [f.as_parameter() for f in fields.values()]
        params = sorted(params, key=lambda p: p.kind)
        return Signature(parameters=params)

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
    def json_func(self):
        return dumps(self)

    @classmethod
    def from_json_func(cls, text):
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
