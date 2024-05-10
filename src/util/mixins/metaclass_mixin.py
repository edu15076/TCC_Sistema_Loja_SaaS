class MetaClassMixin(type):
    @classmethod
    def _is_atribute_in_attrs(cls, attrs, attr_name: str) -> bool:
        return attr_name in attrs

    @classmethod
    def _is_attribute_in_bases(cls, bases, attr_name: str) -> bool:
        for base in bases:
            if attr_name in dir(base):
                return True
        return False

    @classmethod
    def _is_atribute_anywhere(cls, attrs, bases, attr_name: str) -> bool:
        return (cls._is_atribute_in_attrs(attrs, attr_name) or
                cls._is_attribute_in_bases(bases, attr_name))

    @classmethod
    def _find_attribute_in_attrs(cls, attrs, attr_name: str) -> tuple:
        if attr_name in attrs:
            return attrs[attr_name], True
        return None, False

    @classmethod
    def _find_attribute_in_bases(cls, bases, attr_name: str) -> tuple:
        for base in bases:
            if attr_name in dir(base):
                return getattr(base, attr_name), True
        return None, False

    @classmethod
    def _find_attribute_anywhere(cls, attrs, bases, attr_name: str) -> tuple:
        attr, found = cls._find_attribute_in_attrs(attrs, attr_name)
        return (attr, True) if found else cls._find_attribute_in_bases(bases, attr_name)
