# products/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def replace_underscore(value):
    """Replace underscores with spaces in product names"""
    return value.replace('_', ' ')
