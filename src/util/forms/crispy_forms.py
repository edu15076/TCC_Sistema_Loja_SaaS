from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, HTML, Field

from django.utils.translation import gettext_lazy as _

__all__ = (
    'CrispyFormMixin',
    'ModalCrispyFormMixin',
)


class CrispyFormMixin:
    def get_submit_button(self) -> Submit:
        return Submit('submit', _('Submit'))

    def get_fields(self) -> list[Field]:
        return [Field(field) for field in self.fields.keys()]

    def create_helper(self, pass_self=False, add_submit_button=True) -> FormHelper:
        helper = FormHelper() if not pass_self else FormHelper(self)
        helper.form_tag = False
        submit_button = self.get_submit_button()
        if submit_button and add_submit_button:
            helper.add_input(submit_button)
        return helper


class ModalCrispyFormMixin(CrispyFormMixin):
    def create_helper(self, pass_self=False, add_submit_button=True) -> FormHelper:
        helper = super().create_helper(pass_self, False)
        return self._style_modal(helper)

    def _style_modal(self, helper: FormHelper) -> FormHelper:
        helper.layout = Layout(
            Div(
                Div(
                    *self.get_fields(),
                    css_class="modal-body"
                ),
                Div(
                    HTML(
                        f'<button type="button" class="btn btn-secondary"'
                        f' data-bs-dismiss="modal">{_("Close")}</button>'
                    ),
                    self.get_submit_button(),
                    css_class="modal-footer"
                )
            )
        )
        return helper
