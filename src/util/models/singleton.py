from django.db import models

from util.decorators import CachedClassProperty


class NoInstanceError(RuntimeError):
    pass


class SingletonManager(models.Manager):
    def load(self, *args, **kwargs):
        obj, created = self.get_or_create(*args, **kwargs)
        return obj


class AbstractSingleton(models.Model):
    single_instance = SingletonManager()

    @classmethod
    def load(cls, *args, **kwargs):
        return cls.single_instance.load(*args, **kwargs)

    @CachedClassProperty
    def instance(cls):
        try:
            return cls.single_instance.first()
        except SingletonMixin.DoesNotExist:
            raise NoInstanceError(f'No instance exists for {cls.__class__.__name__}')

    @CachedClassProperty
    def instance_pk(cls):
        return cls.instance.pk

    class Meta:
        abstract = True


class SingletonMixin(AbstractSingleton):
    class OnlyChoice(models.IntegerChoices):
        SINGLETON = 1, 'single'

    _singleton = models.SmallIntegerField(
        choices=OnlyChoice.choices,
        default=OnlyChoice.SINGLETON,
        editable=False,
        unique=True,
    )

    class Meta:
        abstract = True
