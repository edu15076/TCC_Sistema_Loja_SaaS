from .metaclass_mixin import MetaClassMixin


class ModelMetaClassMixin(MetaClassMixin):
    @classmethod
    def _is_model_abstract(cls, attrs) -> bool:
        return 'Meta' in attrs and getattr(attrs['Meta'], 'abstract', None)
