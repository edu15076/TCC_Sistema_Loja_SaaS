from django.http import HttpRequest, HttpResponse
from django.views import View

class QueryView(View):
    query_form_class = None

    def search(self, request: HttpRequest, query_form_class=None, queryset=None):
        if query_form_class is None:
            query_form_class = self.query_form_class

        query_form = query_form_class(request.POST)

        if not queryset:
            queryset = self.get_queryset()

        if query_form.is_valid():
            expression = query_form.get_query_expression()
            queryset = queryset.filter(expression)

        return queryset