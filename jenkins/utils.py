from urlparse import urljoin

from django.core.urlresolvers import reverse


def get_notifications_url(base):
    """
    Returns the full URL for notifications given a base.
    """
    return urljoin(base, reverse("jenkins_notifications"))
