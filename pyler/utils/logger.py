import logging


LOG_FORMAT = F"%(asctime)s [%(name)s] %(levelname)s: %(message)s"


class Logger:

    _cache = {}

    @classmethod
    def get_logger(cls, name: str = "default", log_level=None, log_format=LOG_FORMAT):

        def _get_logger():
            logger_format = logging.Formatter(log_format)
            handler = logging.StreamHandler()
            handler.setFormatter(logger_format)
            handler.setLevel(log_level or logging.INFO)
            _logger = logging.Logger(name)
            _logger.addHandler(handler)
            _logger.setLevel(log_level or logging.INFO)
            cls._cache[key] = _logger
            return _logger
        key = (name, log_format)
        return cls._cache.get(key, None) or _get_logger()


get_logger = Logger.get_logger
