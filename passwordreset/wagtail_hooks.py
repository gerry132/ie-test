from django.urls import path
from wagtail import hooks

from .views import force_password_reset


@hooks.register('register_admin_urls')
def register_calendar_url():
    return [
        path('forcepwreset/', force_password_reset, name='force_password_reset'),
    ]
