from django.utils.deprecation import MiddlewareMixin

from datetime import datetime, timedelta


class CustomMiddleware(MiddlewareMixin):

    def _call_(self, request):

        # Code that is executed in each request before the view is called

        response = self.get_response(request)

        # Code that is executed in each request after the view is called
        if 'logout' in request.get_raw_uri():
            login_expire_at = datetime.utcnow() - timedelta(minutes=1)
            response.set_cookie('logout_at', login_expire_at.isoformat() + 'Z')
            response.set_cookie('user_logged_in', False)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # This code is executed just before the view is called
        pass

    def process_response(self, request, response):
        if request.user.is_authenticated:
            response = self.add_logout_expiry(response)
            response.set_cookie('user_logged_in', True)
        return response

    def process_exception(self, request, exception):
        print(exception)

    def add_logout_expiry(self, response):
        login_expire_at = datetime.utcnow() + timedelta(hours=1)
        response.set_cookie('logout_at', login_expire_at.isoformat() + 'Z')
        return response
