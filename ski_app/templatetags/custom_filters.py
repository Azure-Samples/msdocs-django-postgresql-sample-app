from django import template

register = template.Library()

@register.filter
def index(value, i):
    try:
        return value[i]
    except (IndexError, TypeError):
        return None
