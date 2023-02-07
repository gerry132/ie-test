from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect


class IsUserAdmin(MiddlewareMixin):

    def _call_(self, request):

        # Code that is executed in each request before the view is called

        response = self.get_response(request)
        # Code that is executed in each request after the view is called
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # This code is executed just before the view is called
        pass

    def process_response(self, request, response):
        if request.user.is_authenticated:
            if not request.user.is_superuser and '/admin/account/' in request.get_raw_uri():
                return redirect('/admin/account_na/')
        return response

    def process_exception(self, request, exception):
        print(exception)
