from .class_property import ClassProperty
from functools import cache


def CachedClassProperty(method):
    return ClassProperty(cache(method))
    # TODO: Revise code to improve performance
