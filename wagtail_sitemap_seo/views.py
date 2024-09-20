from django.shortcuts import HttpResponse, render
from django.views import View
import os

class SiteMapView(View):

    def get(self, request, file_name, content_type='application/xml'):
        print(12345)
        print(12345)
        print(request.get_full_path())
        file_name = request.get_full_path().replace('/sitemap/', '')

        return HttpResponse(open(file_name + ".xml").read(), content_type='text/xml')
