from crispy_forms.layout import Submit
from django.forms import BaseForm
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.translation import gettext_lazy as _


class NameFormMixin:
    _name = None

    @classmethod
    def submit_name(cls):
        if not cls._name:
            return 'submit'
        return f"{cls._name}_submit"

    @classmethod
    def form_name(cls):
        if not cls._name:
            return 'form'
        return f"{cls._name}_form"

    def get_submit_button(self) -> Submit:
        return Submit(self.submit_name, _('Submit'))


class MultipleFormsViewMixin:
    forms_class = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        forms = self.get_forms()

        for form in forms.values():
            context[form.form_name()] = form

        return context

    def get_forms(self, request: HttpRequest = None):
        forms = {}

        for key, form in self.forms_class.items():
            forms[key] = self.get_form(form_class=form, request=request)

        return forms

    def get_form_class(self, request: HttpRequest):
        for form in self.forms_class.values():
            if form.submit_name() in request.POST:
                return form
        return None

    def get_form_kwargs(self, form_class=None, request=None) -> dict[str, any]:
        kwargs = super().get_form_kwargs()
        return kwargs

    def get_form(
        self, form_class=None, form_name: str = None, request: HttpRequest = None
    ) -> BaseForm:
        if form_class is None and form_name:
            form_class = self.forms_class[form_name]
        elif form_class is None and request:
            for form in self.forms_class.values():
                if form.submit_name() in request.POST:
                    form_class = form
                    break

        if form_class is None:
            return None

        return form_class(**self.get_form_kwargs(form_class, request))

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            form = self.get_form(request=request)

            if form.is_valid():
                return self.form_valid(form)

            return self.form_invalid(form)
        except Exception as e:
            # TODO - Log error
            return JsonResponse(
                {'success': False, 'type': 'error', 'message': str(e)}, status=400
            )
