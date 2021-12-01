# -*- coding: utf-8 -*-
from django.utils.translation import gettext as _
from django.shortcuts import render

from .conf import settings


def get_error_response(request, message, status):
    return render(
        request,
        settings.ERROR_TEMPLATE,
        context={
            'message': message,
            'status': status,
        },
        status=status
    )


def handle_error_403(request, exception):
    status = 403
    message = _('403 happened')
    return get_error_response(request, message, status)


def handle_error_404(request, exception):
    status = 404
    message = _('404 happened')
    return get_error_response(request, message, status)


def handle_error_500(request):
    status = 500
    message = _('500 happened')
    return get_error_response(request, message, status)
