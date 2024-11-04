from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.generic import CreateView, UpdateView
from django.views.generic.edit import ModelFormMixin, FormMixin

__all__ = (
    'CreateHTMXView',
    'UpdateHTMXView',
    'HttpResponseHTMXRedirect',
    'HTMXModelFormMixin',
    'HTMXFormMixin',
)


class HttpResponseHTMXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['HX-Redirect'] = self['Location']

    status_code = 200


class HTMXFormMixin(FormMixin):
    form_action: str = None
    form_template_name: str = 'forms/htmx_form_post_template.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.form_action:
            self.extra_context = self.extra_context or {}
            self.extra_context.update({'action': self.form_action})

    def form_invalid(self, form):
        print('AAAAAAAAAAAA')
        return TemplateResponse(self.request, self.form_template_name,
                                self.get_context_data(form=form))

    def form_valid(self, form):
        return HttpResponseHTMXRedirect(self.get_success_url())


class HTMXModelFormMixin(HTMXFormMixin, ModelFormMixin):
    def form_valid(self, form):
        self.object = form.save()
        a = super().form_valid(form)
        print(f'htmx {a}')
        return a


class CreateHTMXView(HTMXModelFormMixin, CreateView):
    pass


class UpdateHTMXView(HTMXModelFormMixin, UpdateView):
    pass
