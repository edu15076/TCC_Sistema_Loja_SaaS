from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from scope_auth.models.scope import Scope
from scope_auth.models.username_per_scope import AbstractUsernamePerScope
from util.decorators import ClassProperty
from util.mixins import ModelMetaClassMixin


class BaseUserPerScopeManager(BaseUserManager):
    use_in_migrations = True

    def _pop_username_from(self, kwargs):
        return kwargs.pop('username', kwargs.pop(self.model.USERNAME_ACTUAL_FIELD,
                                                 None))

    def _get_username_per_scope_cls_and_manager(self):
        username_per_scope_cls = self.model.get_username_per_scope_type()
        return username_per_scope_cls, username_per_scope_cls._default_manager

    def get_by_natural_key(self, *args, **kwargs):
        """
        get_by_natural_key(username_per_scope_pk) -> UserPerScope
        get_by_natural_key(username, scope) -> UserPerScope

        get_by_natural_key(username_per_scope_pk) -> UserPerScope
        This overload requires username_per_scope_pk to be passed and the
        username_per_scope instance for the username_per_scope_pk passed must
        already exist.

        get_by_natural_key(username, scope) -> UserPerScope
        This version will find the username_per_scope instance for the username and
        scope passed, the instance must already exist. Note that scope must be
        passed by keyword arguments. If scope is None it will default to the
        default_scope.

        :return: The UserPerScope instance corresponding for the passed atributes.
        """
        if len(args) > 1:
            raise ValueError('Only username can be passed as an argument')
        elif len(args) == 1:
            username = args[0]
        else:
            username = self._pop_username_from(kwargs)

        if len(kwargs) > 1 or (len(kwargs) == 1 and 'scope' not in kwargs):
            raise ValueError('The only keyword argument accepted is "scope"')

        _, username_per_scope_manager = self._get_username_per_scope_cls_and_manager()

        if 'scope' not in kwargs:
            username_per_scope = username_per_scope_manager.get(pk=username)
        else:
            username_per_scope = username_per_scope_manager.get_by_natural_key(
                username=username, scope=kwargs.pop('scope', None)
            )

        return self.get(**{self.model.USERNAME_PER_SCOPE_FIELD: username_per_scope})

    def create_by_natural_key(self, **kwargs):
        username = self._pop_username_from(kwargs)
        if username is None:
            raise ValueError(f'Either username or {self.model.USERNAME_ACTUAL_FIELD} '
                             f'should be passed.')
        scope = kwargs.pop('scope', None)
        username_per_scope_extra_fields = kwargs.pop('username_per_scope_extra_fields',
                                                     {})
        _, username_per_scope_manager = self._get_username_per_scope_cls_and_manager()

        username_per_scope = username_per_scope_manager.create_by_natural_key(
            username=username, scope=scope, **username_per_scope_extra_fields
        )
        return self.create(
            **({self.model.USERNAME_PER_SCOPE_FIELD: username_per_scope} | kwargs))


class BaseUserPerScopeMeta(type(AbstractBaseUser), ModelMetaClassMixin):
    def __new__(cls, name, bases, attrs, **kwargs):
        self = super().__new__(cls, name, bases, attrs, **kwargs)

        if self._meta.abstract:
            return self

        username_per_scope_field, found = (
            cls._find_attribute(attrs, bases,
                                         'USERNAME_PER_SCOPE_FIELD'))
        if not found:
            raise ValueError('Non abstract subclass or superclass must define '
                             'USERNAME_PER_SCOPE_FIELD')

        username_per_scope, found = cls._find_field_for_name(self,
                                                             username_per_scope_field)
        if not found:
            raise ValueError(f'Non abstract subclass or superclass must define '
                             f'{username_per_scope_field} for it defined '
                             f'USERNAME_PER_SCOPE_FIELD = {username_per_scope_field}')

        if not username_per_scope.one_to_one:
            if username_per_scope.is_relation:
                raise ValueError(
                    f'{username_per_scope_field} must define a one-to-one relationship '
                    f'with {username_per_scope.remote_field.model.__name__}'
                )
            else:
                raise ValueError(f'{username_per_scope_field} must define a one-to-one '
                                 f'relationship')

        if not username_per_scope.unique:
            raise ValueError(f'{username_per_scope_field} must be unique')

        return self


class AbstractBaseUserPerScope(AbstractBaseUser,
                               metaclass=BaseUserPerScopeMeta):
    users = BaseUserPerScopeManager()

    def get_username_per_scope(self) -> AbstractUsernamePerScope:
        return getattr(self, self.USERNAME_PER_SCOPE_FIELD)

    def get_scope(self) -> Scope:
        return self.get_username_per_scope().scope

    def get_username(self):
        return self.get_username_per_scope().get_username()

    def natural_key(self):
        return self.get_username(), self.get_scope()

    @classmethod
    def get_username_per_scope_type(cls) -> type[AbstractUsernamePerScope]:
        return getattr(cls, cls.USERNAME_PER_SCOPE_FIELD).field.remote_field.model

    @ClassProperty
    def USERNAME_ACTUAL_FIELD(cls):
        return cls.get_username_per_scope_type().USERNAME_FIELD

    @ClassProperty
    def USERNAME_FIELD(cls):
        return cls.USERNAME_PER_SCOPE_FIELD

    class Meta:
        abstract = True


class UserPerScopeManager(BaseUserPerScopeManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")

        _, username_per_scope_manager = self._get_username_per_scope_cls_and_manager()

        if 'scope' in extra_fields:
            user = self.create_by_natural_key(
                username=username, scope=extra_fields.pop('scope'), **extra_fields)
        else:
            username_per_scope = username_per_scope_manager.get(pk=username)
            user = self.create(**({self.model.USERNAME_FIELD: username_per_scope} |
                                  extra_fields))

        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def _validade_username(self, kwargs):
        username_field = self.model.USERNAME_ACTUAL_FIELD
        username_per_scope_field = self.model.USERNAME_PER_SCOPE_FIELD

        scope_is_set = 'scope' in kwargs
        username_is_set = 'username' in kwargs or username_field in kwargs
        username_field_is_set = username_per_scope_field in kwargs

        if not username_is_set and not username_field_is_set:
            raise ValueError(f'Either ((username or {username_field}) and scope) or '
                             f'{username_per_scope_field} should be set, but not both')

        if ('username' == username_per_scope_field or
                username_field == username_per_scope_field):
            return kwargs.pop(username_per_scope_field)

        if username_is_set and username_field_is_set:
            raise ValueError(f'Either ((username or {username_field}) and scope) or '
                             f'{username_per_scope_field} should be set, but not both')

        if username_is_set:
            if not scope_is_set:
                kwargs['scope'] = None
            return self._pop_username_from(kwargs)

        return kwargs.pop(username_per_scope_field)

    def _get_arguments_for_create_user(self, kwargs):
        username = self._validade_username(kwargs)
        password = kwargs.pop('password', None)

        return username, password, kwargs

    def create_user(self, **kwargs):
        username, password, extra_fields = self._get_arguments_for_create_user(kwargs)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, **kwargs):
        username, password, extra_fields = self._get_arguments_for_create_user(kwargs)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        scope_is_set = 'scope' in extra_fields

        if scope_is_set:
            if extra_fields['scope'] is None:
                extra_fields['scope'] = Scope.scopes.default_scope()
            elif not extra_fields['scope'].is_default_scope():
                raise ValueError('Superuser must have scope=default_scope.')
        else:
            _, username_per_scope_manager = (
                self._get_username_per_scope_cls_and_manager())
            scope = username_per_scope_manager.get(pk=username).scope
            if not scope.is_default_scope():
                raise ValueError('Superuser must have scope=default_scope.')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, password, **extra_fields)

    def with_perm(
            self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class AbstractUserPerScope(AbstractBaseUserPerScope, PermissionsMixin):
    """
    This class should not be inherited if it is desired to use email as username,
    inherit from AbstractBaseUserPerScope instead.
    """

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    users = UserPerScopeManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True


class UserPerScopeWhitEmailManager(UserPerScopeManager):
    def _create_user(self, username, password, **kwargs):
        email = kwargs.pop('email', None)
        email = self.normalize_email(email)
        kwargs['email'] = email
        super()._create_user(username, password, **kwargs)


class UserPerScopeWithEmailMeta(BaseUserPerScopeMeta):
    def __new__(cls, name, bases, attrs, **kwargs):
        self = super().__new__(cls, name, bases, attrs, **kwargs)
        if self._meta.abstract:
            return self
        if not cls._has_field(self, 'email'):
            raise ValueError('Subclass must define email')
        return self


class AbstractUserPerScopeWithEmail(AbstractUserPerScope,
                                    metaclass=UserPerScopeWithEmailMeta):
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    class Meta:
        abstract = True
