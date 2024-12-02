from django import forms
from django.utils.translation import gettext_lazy as _

__all__ = (
    'LojaEqualRequiredValidator',
    'NotAdminValidator',
    'ActiveFuncionarioValidator',
)


class LojaEqualRequiredValidator:
    """Validator to ensure the object belongs to the specified loja."""
    error_messages = {
        'field_not_from_loja': _('%(field_name) não existe nessa loja'),
    }

    def __init__(self, loja):
        if loja is None:
            raise ValueError("You must specify a 'loja' to use this validator.")
        self.loja = loja

    def __call__(self, value):
        """Validate if the field's value belongs to the correct loja."""
        if value is None:
            return

        try:
            # If it's a model instance, check if the loja matches
            if not hasattr(value, 'loja') or value.loja != self.loja:
                raise forms.ValidationError(
                    self.error_messages['field_not_from_loja'],
                    code='field_not_from_loja',
                    params={'field_name': value.__class__.__name__},
                )
        except AttributeError:
            raise forms.ValidationError(
                _('Invalid field value'),
                code='invalid'
            )


class NotAdminValidator:
    """Validator to ensure the user is not an admin."""
    error_messages = {
        'funcionario_admin':
            _('O funcionário não pode ser um admin para realizar essa ação'),
    }

    def __call__(self, value):
        if value is None:
            return

        if value.is_admin:
            raise forms.ValidationError(
                self.error_messages['funcionario_admin'],
                code='funcionario_admin'
            )


class ActiveFuncionarioValidator:
    error_messages = {
        'funcionario_not_active':
            _('O funcionário deve estar ativo para realizar essa ação'),
    }

    def __call__(self, value):
        if value is None:
            return

        if not value.is_active:
            raise forms.ValidationError(
                self.error_messages['funcionario_not_active'],
                code='funcionario_not_active'
            )


class SelfValidator:
    error_messages = {
        'self_not_allowed': _('You cannot perform this action on yourself'),
    }

    def __init__(self, myself=None):
        self.myself = myself

    def __call__(self, value):
        if value is None or self.myself is None:
            return

        if value == self.myself:
            raise forms.ValidationError(
                self.error_messages['self_not_allowed'],
                code='self_not_allowed'
            )
