from django.urls import path
from irelandie_api.views.news import NewsPageAPIView
from .views.pagination import api_pagination_partial


urlpatterns = [
    path("news/", NewsPageAPIView.as_view(), name="news-api"),
    path("api-pagination/", api_pagination_partial, name="api-pagination"),
]
