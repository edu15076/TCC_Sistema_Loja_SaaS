from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from scope_auth.models.scope import Scope
from scope_auth.models.username_per_scope import AbstractUsernamePerScope
from util import AbstractBuilder
from util.decorators import ClassProperty, CachedProperty
from util.mixins import ModelMetaClassMixin


class BaseUserPerScopeManager(BaseUserManager):
    use_in_migrations = True

    def _pop_username_from(self, kwargs):
        return kwargs.pop(
            'username', kwargs.pop(self.model.USERNAME_ACTUAL_FIELD, None)
        )

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

        username_per_scope_cls, username_per_scope_manager = (
            self._get_username_per_scope_cls_and_manager()
        )

        try:
            if 'scope' not in kwargs:
                username_per_scope = username_per_scope_manager.get(pk=username)
            else:
                username_per_scope = username_per_scope_manager.get_by_natural_key(
                    username=username, scope=kwargs.pop('scope', None)
                )
        except username_per_scope_cls.DoesNotExist:
            raise self.model.DoesNotExist

        return self.get(**{self.model.USERNAME_PER_SCOPE_FIELD: username_per_scope})


class BaseUserPerScopeMeta(type(AbstractBaseUser), ModelMetaClassMixin):
    def __new__(cls, name, bases, attrs, **kwargs):
        self = super().__new__(cls, name, bases, attrs, **kwargs)

        if self._meta.abstract:
            return self

        username_per_scope_field, found = cls._find_attribute(
            attrs, bases, 'USERNAME_PER_SCOPE_FIELD'
        )
        if not found:
            raise ValueError(
                'Non abstract subclass or superclass must define '
                'USERNAME_PER_SCOPE_FIELD'
            )

        username_per_scope, found = cls._find_field_for_name(
            self, username_per_scope_field
        )
        if not found:
            raise ValueError(
                f'Non abstract subclass or superclass must define '
                f'{username_per_scope_field} for it defined '
                f'USERNAME_PER_SCOPE_FIELD = {username_per_scope_field}'
            )

        if not username_per_scope.one_to_one:
            if username_per_scope.is_relation:
                raise ValueError(
                    f'{username_per_scope_field} must define a one-to-one relationship '
                    f'with {username_per_scope.remote_field.model.__name__}'
                )
            else:
                raise ValueError(
                    f'{username_per_scope_field} must define a one-to-one '
                    f'relationship'
                )

        if not username_per_scope.unique:
            raise ValueError(f'{username_per_scope_field} must be unique')

        return self


class AbstractBaseUserPerScope(AbstractBaseUser, metaclass=BaseUserPerScopeMeta):
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

    def clean(self):
        pass

    def delete(self, *args, **kwargs):
        related_username_per_scope = self.get_username_per_scope()
        delete_result = super().delete(*args, **kwargs)
        delete_related_result = related_username_per_scope.delete()
        return (
            delete_result[0] + delete_related_result[0],
            delete_result[1] | delete_related_result[1]
        )

    class Meta:
        abstract = True


class UserPerScopeManager(BaseUserPerScopeManager):
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        try:
            if not username:
                raise KeyError("'username' must be set.")

            user = self.model(**{self.model.USERNAME_FIELD: username}, **extra_fields)
            user.password = make_password(password)
            user.full_clean()
            user.save(using=self._db)
        except ValidationError as e:
            username.delete()
            raise e

        return user

    def _validate_username_per_scope_natural_key(self, kwargs: dict) -> tuple:
        username_field = self.model.USERNAME_ACTUAL_FIELD

        if username_field not in kwargs:
            raise KeyError(f"'{username_field}' must be set.")

        username = kwargs.pop(username_field)
        scope = kwargs.pop('scope', None)

        if scope is None:
            scope = Scope.scopes.default_scope()

        return username, scope, kwargs

    def _create_username_per_scope_by_natural_key(
        self, kwargs: dict
    ) -> AbstractUsernamePerScope:
        username, scope, kwargs = self._validate_username_per_scope_natural_key(kwargs)

        _, username_per_scope_manager = self._get_username_per_scope_cls_and_manager()

        return username_per_scope_manager.create_username_per_scope(
            username=username,
            scope=scope,
            **kwargs.pop('username_per_scope_extra_fields', {}),
        )

    def _get_username_per_scope_by_natural_key(
        self, kwargs: dict
    ) -> AbstractUsernamePerScope:
        username, scope, kwargs = self._validate_username_per_scope_natural_key(kwargs)
        if 'username_per_scope_extra_fields' in kwargs:
            raise KeyError("'username_per_scope_extra_fields' should not be set.")

        _, username_per_scope_manager = self._get_username_per_scope_cls_and_manager()

        return username_per_scope_manager.get_by_natural_key(
            username=username, scope=scope
        )

    def _get_username_per_scope(self, kwargs: dict) -> AbstractUsernamePerScope:
        username_per_scope_field = self.model.USERNAME_PER_SCOPE_FIELD

        if username_per_scope_field not in kwargs:
            raise KeyError(f"'{username_per_scope_field}' must be set.")

        username_per_scope_pk = kwargs.pop(username_per_scope_field)
        _, username_per_scope_manager = self._get_username_per_scope_cls_and_manager()
        return username_per_scope_manager.get(pk=username_per_scope_pk)

    def _get_arguments_for_create_user(self, kwargs):
        username = self._get_username_per_scope(kwargs)
        password = kwargs.pop('password', None)

        return username, password, kwargs

    def _get_cleaned_user(self, kwargs):
        username, password, extra_fields = self._get_arguments_for_create_user(kwargs)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return username, password, extra_fields

    def create_user(self, **kwargs):
        """
        Create a new user with the provided parameters.

        **Required Parameters:**

        * `password`: The password for the new user.

        * `UserPerScope.USERNAME_PER_SCOPE_FIELD`: The primary key of the
          `UsernamePerScope` instance for the new user (alternative to `username` or
          `UsernamePerScope.USERNAME_FIELD`).

        **Optional Parameters:**

        * Any additional fields can be passed as keyword arguments.

        :param kwargs: Parameters as specified above.
        :return: A new user.
        :raises KeyErro: If `password` is not set or if neither of the username
            options are set or if the first username option is set but `scope` is not.
        """
        username, password, extra_fields = self._get_cleaned_user(kwargs)
        return self._create_user(username, password, **extra_fields)

    def _get_cleaned_superuser(self, kwargs):
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
                self._get_username_per_scope_cls_and_manager()
            )
            scope = username.scope
            if not scope.is_default_scope():
                raise ValueError('Superuser must have scope=default_scope.')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return username, password, extra_fields

    def create_superuser(self, **kwargs):
        """
        Create a new superuser with the provided parameters.

        **Required Parameters:**

        * `password`: The password for the new superuser.

        * `UserPerScope.USERNAME_PER_SCOPE_FIELD`: The primary key of the
          `UsernamePerScope` instance for the new user (alternative to `username` or
          `UsernamePerScope.USERNAME_FIELD`).

        **Optional Parameters:**

        * Any additional fields can be passed as keyword arguments.

        :param kwargs: Parameters as specified above.
        :return: A new superuser.
        :raises KeyError: If `password` is not set or if neither of the username
            options are set or if the first username option is set but `scope` is not.
        """
        username, password, extra_fields = self._get_cleaned_superuser(kwargs)
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

    def create_user_by_natural_key(self, **kwargs):
        """
        Create a new user with the provided parameters.

        **Required Parameters:**

        * `password`: The password for the new user.

        * `username` or the value of `UsernamePerScope.USERNAME_FIELD`: The value for
          the attribute named `UsernamePerScope.USERNAME_FIELD` in `UsernamePerScope`.

        **Optional Parameters:**

        * `scope`: The scope of the new user, if not set the default scope will be used.

        * Any additional fields can be passed as keyword arguments.  One of which can be
          `username_per_scope_extra_fields`, passing a `dict` for any extra fields to
          create a username per scope instance for the new user.

        :param kwargs: Parameters as specified above.
        :return: A new user.
        :raises KeyError: If `password` is not set or if neither of the username
            options are set or if the first username option is set but `scope` is not.
        """
        username = self._create_username_per_scope_by_natural_key(kwargs).pk
        kwargs[self.model.USERNAME_PER_SCOPE_FIELD] = username
        return self.create_user(**kwargs)

    def create_superuser_by_natural_key(self, **kwargs):
        """
        Create a new superuser with the provided parameters.

        **Required Parameters:**

        * `password`: The password for the new superuser.

        * The attribute with value of `UsernamePerScope.USERNAME_FIELD`: The value for
          the attribute named `UsernamePerScope.USERNAME_FIELD` in `UsernamePerScope`.

        **Optional Parameters:**

        * `scope`: The scope of the new superuser, if not set the default scope will be
          used.

        * Any additional fields can be passed as keyword arguments.  One of which can be
          `username_per_scope_extra_fields`, passing a `dict` for any extra fields to
          create a username per scope instance for the new superuser.

        :param kwargs: Parameters as specified above.
        :return: A new superuser.
        :raises KeyError: If `password` is not set or if neither of the username
            options are set or if the first username option is set but `scope` is not.
        """
        username = self._create_username_per_scope_by_natural_key(kwargs).pk
        kwargs[self.model.USERNAME_PER_SCOPE_FIELD] = username
        return self.create_superuser(**kwargs)

    def _get_or_create_username_from_kwargs(self, kwargs):
        kwargs_cpy = kwargs.copy()
        username_per_scope_model, _ = self._get_username_per_scope_cls_and_manager()
        try:
            username = self._get_username_per_scope_by_natural_key(kwargs)
            return username, True
        except username_per_scope_model.DoesNotExist:
            kwargs = kwargs_cpy
            username = self._create_username_per_scope_by_natural_key(kwargs)
            return username, False

    def create_or_reactivate_user(self, **kwargs):
        """
        If user does not exist, create a new user. Otherwise, reactivate the user
        :param kwargs:
        :return:
        """
        username, exists = self._get_or_create_username_from_kwargs(kwargs)

        if not exists:
            return self.create_user(
                **{self.model.USERNAME_PER_SCOPE_FIELD: username}, **kwargs
            )
        else:
            user = self.get_by_natural_key(
                **{self.model.USERNAME_PER_SCOPE_FIELD: username}
            )
            user.reactivate(commit=False)
            return user

    def create_builder(self):
        return self._Builder(self.model)

    class _Builder(AbstractBuilder):
        """Allows to create user from this builder."""

        def __init__(self, user_type):
            super().__init__()
            self._user_type = user_type

        @CachedProperty
        def _manager(self) -> 'UserPerScopeManager':
            return self._user_type._meta.default_manager

        def build_user(self):
            return self._manager.create_user(**self._kwargs)

        def build_user_by_natural_key(self):
            return self._manager.create_user_by_natural_key(**self._kwargs)

        def build_superuser(self):
            return self._manager.create_superuser(**self._kwargs)

        def build_superuser_by_natural_key(self):
            return self._manager.create_superuser_by_natural_key(**self._kwargs)

        def build(self):
            """The default builder builds a user by its natural key."""
            return self.build_user_by_natural_key()


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

    def reactivate(self, commit=True):
        if self.is_active:
            raise ValueError('User is already active.')
        self.is_active = True
        if commit:
            self.save()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = True


class UserPerScopeWhitEmailManager(UserPerScopeManager):
    def _create_user(self, username, password, **kwargs):
        kwargs['email'] = self.normalize_email(kwargs.get('email', None))
        return super()._create_user(username, password, **kwargs)


class UserPerScopeWithEmailMeta(BaseUserPerScopeMeta):
    def __new__(cls, name, bases, attrs, **kwargs):
        self = super().__new__(cls, name, bases, attrs, **kwargs)
        if self._meta.abstract:
            return self
        if not cls._has_field(self, 'email'):
            raise TypeError('Subclass must define email')
        return self


class AbstractUserPerScopeWithEmail(
    AbstractUserPerScope, metaclass=UserPerScopeWithEmailMeta
):
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def clean(self):
        super().clean()
        self.email = self._meta.default_manager.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    class Meta:
        abstract = True
