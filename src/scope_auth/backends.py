from django.contrib.auth.backends import ModelBackend, UserModel
from .util import get_scope_from_request


class ModelScopeBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return

        scope = (
            get_scope_from_request(request)
            if kwargs.get('scope') is None
            else kwargs['scope']
        )
        if scope is None:
            return

        try:
            user = UserModel._default_manager.get_by_natural_key(
                username=username, scope=scope
            )
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
