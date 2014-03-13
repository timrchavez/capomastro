from datetime import timedelta

from django.template.base import Library


register = Library()


@register.filter(is_safe=True)
def build_time_to_timedelta(value):
    """Converts a build time in milliseconds to a timedelta."""
    if value is None:
        return ""
    return timedelta(milliseconds=value)
