# -*- coding: utf-8 -*-
from django.conf import settings as dj_settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic import RedirectView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls


PREFIX_DEFAULT_LANGUAGE = getattr(
    dj_settings,
    'PREFIX_DEFAULT_LANGUAGE',
    True
)


urlpatterns = [
    path('', include('health_check.urls')),
    path('django-admin/', admin.site.urls),
    path('admin/', include(wagtailadmin_urls)),
    path('', include(wagtaildocs_urls)),
]


if dj_settings.DEBUG_TOOLBAR is True:

    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]


if dj_settings.USE_S3 is True:
    urlpatterns += staticfiles_urlpatterns()


urlpatterns += static(
    dj_settings.MEDIA_URL,
    document_root=dj_settings.MEDIA_ROOT
)


urlpatterns += i18n_patterns(
    path('', include(wagtail_urls)),
    prefix_default_language=PREFIX_DEFAULT_LANGUAGE,
)


urlpatterns += [
    path(
        '',
        RedirectView.as_view(url=f'/{dj_settings.LANGUAGE_CODE}/'),
        name='no-language-home'
    ),
]


handler404 = 'irelandie_utils.views.page_not_found'
handler500 = 'irelandie_utils.views.server_error'
