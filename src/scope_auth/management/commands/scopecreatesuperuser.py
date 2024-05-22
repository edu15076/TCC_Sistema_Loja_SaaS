from django.contrib.auth.management.commands.createsuperuser import (
    Command as CreateSuperUserCommand)
from django.core import exceptions


class Command(CreateSuperUserCommand):
    def _create_user_from_username(self, username):
        username_per_scope_cls = self.UserModel.get_username_per_scope_type()
        return username_per_scope_cls._default_manager.create_username_per_scope(
            username=username)

    def get_input_data(self, field, message, default=None):
        """
        Override this method if you want to customize data inputs or
        validation exceptions.
        """
        raw_value = input(message)
        if default and raw_value == "":
            raw_value = default
        try:
            if field == self.username_field:
                val = field.clean(self._create_user_from_username(raw_value).pk, None)
            else:
                val = field.clean(raw_value, None)
        except exceptions.ValidationError as e:
            self.stderr.write("Error: %s" % "; ".join(e.messages))
            val = None

        return val
