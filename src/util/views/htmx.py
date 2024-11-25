from django.http import (
    HttpResponseRedirect,
    HttpResponseNotFound,
    JsonResponse
)
from django.template.response import TemplateResponse
from django.urls import resolve
from django.views.generic import CreateView, UpdateView
from django.views.generic.base import ContextMixin, TemplateView
from django.views.generic.edit import ModelFormMixin, FormMixin

__all__ = (
    'CreateHTMXView',
    'UpdateHTMXView',
    'HttpResponseHTMXRedirect',
    'HTMXModelFormMixin',
    'HTMXFormMixin',
    'HTMXHelperMixin',
    'HTMXTemplateView',
)


class HttpResponseHTMXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self['HX-Redirect'] = self['Location']

    status_code = 200


class HTMXHelperMixin(ContextMixin):
    restrict_direct_access = False

    def is_htmx_request(self):
        return bool(self.request.headers.get('HX-Request'))

    def should_block_request(self):
        return self.restrict_direct_access and not self.is_htmx_request()


class HTMXTemplateView(HTMXHelperMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        if self.should_block_request():
            return HttpResponseNotFound()
        return super().get(request, *args, **kwargs)


class HTMXFormMixin(HTMXHelperMixin, FormMixin):
    form_action: str = None
    form_template_name: str = 'forms/htmx_form_post_template.html'
    redirect_on_success = True
    hx_target_form_invalid = 'this'
    hx_target_form_valid = 'this'

    def get_hx_target_form_invalid(self):
        return self.hx_target_form_invalid

    def get_hx_target_form_valid(self):
        return self.hx_target_form_valid

    def get_form_action(self):
        return self.form_action

    def get_context_data(self, **kwargs):
        if self.get_form_action():
            kwargs['action'] = self.get_form_action()
        return super().get_context_data(**kwargs)

    def form_invalid(self, form):
        response = TemplateResponse(
            self.request, self.form_template_name, self.get_context_data(form=form)
        )
        response['HX-Retarget'] = self.get_hx_target_form_invalid()
        response['HX-Reswap'] = 'outerHTML'
        return response

    def form_valid(self, form):
        if self.get_success_url() is None:
            return JsonResponse({'status': True}, status=200)
        if self.redirect_on_success:
            return HttpResponseHTMXRedirect(self.get_success_url())

        self.request.method = 'GET'
        match = resolve(self.get_success_url())
        response = match.func(self.request, *match.args, **match.kwargs)
        if not self.request.headers.get('HX-Request'):
            response['HX-Retarget'] = self.get_hx_target_form_valid()
        return response


class HTMXModelFormMixin(HTMXFormMixin, ModelFormMixin):
    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)


class CreateHTMXView(HTMXModelFormMixin, CreateView):
    def get(self, request, *args, **kwargs):
        if not self.should_block_request():
            return super().get(request, *args, **kwargs)
        return HttpResponseNotFound()



class UpdateHTMXView(HTMXModelFormMixin, UpdateView):
    def get(self, request, *args, **kwargs):
        if not self.should_block_request():
            return super().get(request, *args, **kwargs)
        return HttpResponseNotFound()
