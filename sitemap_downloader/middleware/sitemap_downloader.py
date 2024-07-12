from django.utils.deprecation import MiddlewareMixin
from irelandie_utils.views import page_not_found

from django.http import HttpResponseForbidden


class CustomLoginChecker(MiddlewareMixin):

    def _call_(self, request):

        # Code that is executed in each request before the view is called

        response = self.get_response(request)

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # This code is executed just before the view is called
        pass

    def process_response(self, request, response):
        sitemap_whitelist = ['85.208.98.128', '85.208.98.53', '85.208.98.0',
                             '46.229.173.67', '46.229.173.66', '46.229.173.68',
                             '85.208.98.194', '85.208.98.224']
        origin_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        print(request.is_secure())
        if request.path == '/sitemap.xml':
            if request.user.is_authenticated or origin_ip in sitemap_whitelist:
                return response
            else:
                return page_not_found(request, None)
        elif origin_ip in sitemap_whitelist:
            return HttpResponseForbidden()
        return response

    def process_exception(self, request, exception):
        print(exception)
