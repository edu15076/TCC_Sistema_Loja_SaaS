class CachedProperty:
    def __init__(self, f):
        self._f = f
        self._value = None

    def __get__(self, instance, owner):
        if self._value is None:
            self._value = self._f(instance)
        return self._value
