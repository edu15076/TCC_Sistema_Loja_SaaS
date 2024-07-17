from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect


__all__ = ('NotLoggedInRequiredMixin',)


class NotLoggedInRequiredMixin(UserPassesTestMixin):
    redirect_url_if_user_is_logged_in = '/'

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return HttpResponseRedirect(self.redirect_url_if_user_is_logged_in)
