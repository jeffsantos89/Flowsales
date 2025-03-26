import threading
from contextlib import contextmanager


class RequestContext:
    _request_data = threading.local()

    @classmethod
    def set(cls, key, value):
        if not hasattr(cls._request_data, 'data'):
            cls._request_data.data = {}
        cls._request_data.data[key] = value

    @classmethod
    def get(cls, key, default=None):
        if not hasattr(cls._request_data, 'data'):
            return default
        return cls._request_data.data.get(key, default)

    @classmethod
    def clear(cls):
        if hasattr(cls._request_data, 'data'):
            cls._request_data.data.clear()

    @classmethod
    def all(cls):
        if not hasattr(cls._request_data, 'data'):
            return {}
        return cls._request_data.data

@contextmanager
def request_context(**kwargs):
    try:
        for key, value in kwargs.items():
            RequestContext.set(key, value)
        yield
    finally:
        RequestContext.clear()