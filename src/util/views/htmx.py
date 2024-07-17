from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.generic import CreateView

__all__ = (
    'CreateHTMXView',
    'HttpResponseHTMXRedirect',
)


class HttpResponseHTMXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['HX-Redirect'] = self['Location']

    status_code = 200


class CreateHTMXView(CreateView):
    form_class: ModelForm = None
    template_name: str = None
    form_template_name: str = None
    redirect_url: str = None

    def form_invalid(self, form):
        return TemplateResponse(self.request, self.form_template_name,
                                self.get_context_data(form=form))

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseHTMXRedirect(self.redirect_url)
