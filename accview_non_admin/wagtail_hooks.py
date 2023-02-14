from django.urls import path
from wagtail import hooks

from .views import account


@hooks.register('register_admin_urls')
def register_calendar_url():
    return [
        path('account_na/', account, name='non admin account'),
    ]
