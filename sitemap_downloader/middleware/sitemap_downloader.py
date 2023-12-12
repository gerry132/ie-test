from django.utils.deprecation import MiddlewareMixin
from irelandie_utils.views import page_not_found


class CustomLoginChecker(MiddlewareMixin):

    def _call_(self, request):

        # Code that is executed in each request before the view is called

        response = self.get_response(request)

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # This code is executed just before the view is called
        pass

    def process_response(self, request, response):
        if request.path == '/sitemap.xml':
            print('test')
            print('test')
            print('test')
            print('test')
            print('test')
            print('test')
            print('test')
            if request.user.is_authenticated:
                print('user')
                print('user')
                return response
            else:
                print('nope')
                print('nope')
                print('nope')
                print('nope')
                return page_not_found(request, None)
        return response

    def process_exception(self, request, exception):
        print(exception)
