from abc import ABCMeta
from collections.abc import MutableMapping
from copy import deepcopy
from pprint import pformat

from pyler.exceptions import NotSupported, UsageError


class Field(dict):
    pass


class ItemMeta(ABCMeta):

    def __new__(mcs, name, bases, attrs):
        fields = {}
        for attr, value in attrs.items():
            if isinstance(value, Field):
                fields[attr] = value
        cls_instance = super().__new__(mcs, name, bases, attrs)
        cls_instance.fields = fields
        return cls_instance


class Item(MutableMapping, metaclass=ItemMeta):

    fields: Field

    def __init__(self, *args, **kwargs):
        self._values = {}
        if args:
            raise NotSupported(f"{self.__class__.__name__} not support args, use keyword args")
        if kwargs:
            for key, value in kwargs.items():
                self[key] = value

    def __setitem__(self, key, value):
        if key in self.fields:
            self._values[key] = value
        else:
            raise KeyError(f"{self.__class__.__name__}.{key} is not in fields")

    def __getitem__(self, key):
        return self._values[key]

    def __delitem__(self, key):
        del self._values[key]

    def __setattr__(self, key, value):
        if key != '_values':
            raise AttributeError(f"use item[{key!r}] = {value!r} to set field value")
        super().__setattr__(key, value)

    def __getattr__(self, key):
        """当获取不到属性时会触发该方法"""
        raise AttributeError(f"{self.__class__.__name__} not support field: {key!r}")

    def __getattribute__(self, item):
        fields = super().__getattribute__("fields")
        if item in fields:
            raise UsageError(f"use item[{item!r}] to get field value")
        else:
            return super().__getattribute__(item)

    def __iter__(self):
        return iter(self._values)

    def __len__(self):
        return len(self._values)

    def __str__(self):
        return pformat(dict(self._values))

    __repr__ = __str__

    def to_dict(self):
        return dict(self)

    def copy(self):
        return deepcopy(self)
