from django.shortcuts import HttpResponse
from django.views import View


class SiteMapView(View):

    def get(self, request, file_name, content_type='application/xml'):
        file_name = request.get_full_path().replace('/sitemap/', '')
        return HttpResponse(open(file_name + ".xml").read(), content_type='text/xml')
