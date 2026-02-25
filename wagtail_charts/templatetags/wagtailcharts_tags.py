from django import template
from django.template.loader import render_to_string

from uuid import uuid4


register = template.Library()


@register.simple_tag
def render_charts():
    return render_to_string("wagtailcharts/tags/render_charts.html")


@register.simple_tag
def generate_uuid4():
    return uuid4()


@register.filter()
def addspace(val):
    return val.replace("_", " ")

