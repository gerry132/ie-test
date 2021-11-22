# -*- coding: utf-8 -*-
from django.shortcuts import HttpResponse
from django.views import View


class HealthCheckView(View):

    def get(self, request):
        return HttpResponse()
