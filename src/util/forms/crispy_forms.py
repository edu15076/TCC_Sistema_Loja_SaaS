from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


__all__ = (
    'CrispyFormMixin',
)


class CrispyFormMixin:
    def get_submit_button(self) -> Submit:
        return Submit('submit', 'Submit')

    def create_helper(self, pass_self=False) -> FormHelper:
        helper = FormHelper() if not pass_self else FormHelper(self)
        helper.form_tag = False
        submit_button = self.get_submit_button()
        if submit_button:
            helper.add_input(submit_button)
        return helper
