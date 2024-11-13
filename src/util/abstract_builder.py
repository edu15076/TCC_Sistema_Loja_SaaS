from abc import ABC, abstractmethod
from typing_extensions import Self


__all__ = ['AbstractBuilder']


class AbstractBuilder(ABC):
    def __init__(self):
        self._kwargs = {}

    def __setattr__(self, key: str, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            self._kwargs[key] = value

    def __getattr__(self, item):
        if item.startswith('set_'):

            def setter(value) -> Self:
                setattr(self, item[4:], value)
                return self

            return setter
        return super().__getattribute__(item)

    def __repr__(self):
        items = tuple(self._kwargs.items())
        return (
            self.__class__.__name__
            + '('
            + ''.join(tuple(f'{key}={repr(value)}, ' for key, value in items[:-1]))
            + f'{items[-1][0]}={repr(items[-1][1])})'
        )

    def __str__(self):
        return "'" + repr(self) + "'"

    @abstractmethod
    def build(self):
        raise NotImplementedError
