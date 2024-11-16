from django.contrib.auth.mixins import AccessMixin


class ScopeRequiredMixin(AccessMixin):
    def handle_no_permission(self):
        pass
