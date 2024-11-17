class ClassProperty:
    """A classproperty annotation"""

    def __init__(self, f):
        self._f = f

    def __get__(self, instance, owner):
        return self._f(owner)
