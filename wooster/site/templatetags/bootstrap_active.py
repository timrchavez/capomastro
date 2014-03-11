from django import template
from django.core.urlresolvers import reverse

register = template.Library()


@register.simple_tag(takes_context=True)
def active_url(context, path):
    if context["request"].path == reverse(path):
        return "active"
    else:
        return ""

