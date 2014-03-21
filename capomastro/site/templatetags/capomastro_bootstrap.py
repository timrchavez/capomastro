from django.template.base import Library
from django.core.urlresolvers import reverse


register = Library()


@register.filter(is_safe=True)
def build_status_to_class(value):
    """
    Converts a known build status from Jenkins to a bootstrap table class.
    """
    known_statuses = {
        "SUCCESS": "success",
        "FAILURE": "danger",
        "ABORTED": "info"
    }
    return known_statuses.get(value, "")


@register.simple_tag(takes_context=True)
def active_url(context, path):
    if context["request"].path == reverse(path):
        return "active"
    else:
        return ""
