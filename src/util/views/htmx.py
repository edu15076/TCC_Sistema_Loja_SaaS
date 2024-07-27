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
    form_template_name: str = None

    def form_invalid(self, form):
        return TemplateResponse(self.request, self.form_template_name,
                                self.get_context_data(form=form))

    def form_valid(self, form):
        return HttpResponseHTMXRedirect(self.get_success_url())


class HTMXModelFormMixin(HTMXFormMixin, ModelFormMixin):
    form_template_name: str = None

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)


class CreateHTMXView(HTMXModelFormMixin, CreateView):
    pass


class UpdateHTMXView(HTMXModelFormMixin, UpdateView):
    pass
