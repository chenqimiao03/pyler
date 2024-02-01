from importlib import import_module
from typing import Union, Callable


from pyler.settings import Settings


def get_settings(module="settings"):
    _settings = Settings()
    _settings.setmodule(module)
    return _settings


def update_settings(spider, settings):
    if hasattr(spider, "custom_settings"):
        custom_settings = getattr(spider, "custom_settings")
        settings.update(custom_settings)


def load_instance(_path: Union[str, Callable]):
    if not isinstance(_path, str):
        if callable(_path):
            return _path
        raise TypeError(f"args _path must be str or object, but got {type(_path)}")
    filename, cls = _path.rsplit(".", 1)
    module = import_module(filename)
    try:
        cls = getattr(module, cls)
    except AttributeError:
        raise NameError(f"module {filename} not exists or not found ")
    return cls
