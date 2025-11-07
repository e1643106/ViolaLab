from django import template

register = template.Library()


@register.filter
def attr(value, name):
    """Safely access an attribute on an object in templates."""
    if value is None:
        return None
    return getattr(value, name, None)
