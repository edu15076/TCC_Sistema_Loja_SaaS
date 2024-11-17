from crispy_forms.layout import Submit
from django.contrib.auth.forms import PasswordChangeForm

from util.forms import CrispyFormMixin


class PasswordChangeUserPerScopeWithEmailForm(CrispyFormMixin, PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()

    def get_submit_button(self) -> Submit:
        return Submit('alterar', 'Alterar')
