import json
from copy import deepcopy
from types import ModuleType
from typing import Union
from importlib import import_module

from pyler.settings import default_settings


class Settings:

    def __init__(self, values: Union[str, dict, None] = None):
        self.attrs = {}
        self.setmodule(default_settings)
        self.update(values)

    def __getitem__(self, item):
        if item not in self:
            return None
        return self.attrs[item]

    def __contains__(self, item):
        return item in self.attrs

    def __setitem__(self, item, value):
        self.set(item, value)

    def __delitem__(self, item):
        del self.attrs[item]

    def __str__(self):
        return f"<SettingsAttribute value={self.attrs}"

    __repr__ = __str__

    def set(self, name, value):
        self.attrs[name] = value

    def get(self, name, default=None):
        return self[name] if self[name] is not None else default

    def getint(self, name, default=0):
        return int(self.get(name, default))

    def getfloat(self, name, default=0.):
        return float(self.get(name, default))

    def getbool(self, name, default=False): # noqa
        value = self.get(name, default)
        try:
            return bool(int(value))
        except ValueError:
            if value.upper() == 'TRUE':
                return True
            elif value.upper() == 'FALSE':
                return False
            else:
                raise ValueError(
                    f'{name} support value for bool settings are (0 or 1), (True or False), '
                    f'("TRUE" OR "False") but got {value}'
                )

    def getlist(self, name, default=None):
        value = self.get(name, default or [])
        if isinstance(value, str):
            value = value.split(',')
        return list(value)

    def setmodule(self, module: Union[ModuleType, str]) -> None: # noqa
        # 传入模块名称
        if isinstance(module, str):
            module = import_module(module)
        for key in dir(module):
            if key.isupper():
                self.set(key, getattr(module, key))

    def update(self, values):
        if isinstance(values, str):
            values = json.loads(values)
        if values is not None:
            for key, value in values.items():
                self.set(key, value)

    def copy(self):
        return deepcopy(self)
