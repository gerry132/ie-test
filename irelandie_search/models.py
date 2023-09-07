from django.db import models


class SearchTerm(models.Model):
    search_term = models.TextField(null=False)
    count = models.IntegerField(blank=False)
