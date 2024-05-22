from .class_property import ClassProperty


class CachedClassProperty:
    """
    Makes a method work as a classproperty and runs the method only once, as it
    computes the return value on the first call.
    """

    def __init__(self, f):
        self._f = ClassProperty(f)
        self._value = None

    def __get__(self, *args):
        if self._value is None:
            self._value = self._f.__get__(*args)
        return self._value
