from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta


class ForcePasswordReset(MiddlewareMixin):

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
            if request.user.reset_lock and '/admin/forcepwreset/' not in request.get_raw_uri():
                return redirect('/admin/forcepwreset/')
            elif request.POST and '/admin/login/' in request.get_raw_uri():
                user = request.user
                if self.is_expired(user):
                    return redirect('/admin/forcepwreset/')
        return response

    def process_exception(self, request, exception):
        print(exception)

    def is_expired(self, user):
        if not user.password_reset:
            reset_time = timezone.now() + timedelta(minutes=2)
            user.password_reset = reset_time
            user.save()
        elif user.password_reset < timezone.now():
            user.reset_lock = True
            user.save()
            return True
        return False
