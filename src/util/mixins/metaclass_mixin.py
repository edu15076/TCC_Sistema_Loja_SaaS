class MetaClassMixin(type):
    @classmethod
    def _has_atribute_in_attrs(cls, attrs, attr_name: str) -> bool:
        return attr_name in attrs

    @classmethod
    def _has_attribute_in_bases(cls, bases, attr_name: str) -> bool:
        for base in bases:
            if attr_name in dir(base):
                return True
        return False

    @classmethod
    def _has_atribute(cls, attrs, bases, attr_name: str) -> bool:
        return cls._has_atribute_in_attrs(
            attrs, attr_name
        ) or cls._has_attribute_in_bases(bases, attr_name)

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
    def _find_attribute(cls, attrs, bases, attr_name: str) -> tuple:
        attr, found = cls._find_attribute_in_attrs(attrs, attr_name)
        return (attr, True) if found else cls._find_attribute_in_bases(bases, attr_name)

    @classmethod
    def _all_attributes_in_attrs(cls, attrs) -> dict:
        return attrs.copy()

    @classmethod
    def _all_attributes_in_bases(cls, bases) -> dict:
        attributes = {}
        for base in bases:
            attributes.update(vars(base))
        return attributes

    @classmethod
    def _all_attributes(cls, attrs, bases):
        return {
            **cls._all_attributes_in_attrs(attrs),
            **cls._all_attributes_in_bases(bases),
        }
