from rest_framework import serializers
from irelandie_news.models import NewsPage


class NewsPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPage
        fields = ['title', 'subtitle', 'publication_date', 'full_url']
