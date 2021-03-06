from django.template import Template, Context
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

from urlparse import urljoin

from django.core.urlresolvers import reverse


def get_notifications_url(base):
    """
    Returns the full URL for notifications given a base.
    """
    return urljoin(base, reverse("jenkins_notifications"))


def get_context_for_template(job):
    """
    Returns a Context for the Job XML templating.
    """
    defaults = DefaultSettings({"NOTIFICATION_HOST": "http://localhost"})
    context_vars = {
        "notifications_url": get_notifications_url(defaults.NOTIFICATION_HOST),
        "job": job,
        "jobtype": job.jobtype,
    }
    return Context(context_vars)


def get_job_xml_for_upload(job):
    """
    Return config_xml run through the template mechanism.
    """
    template = Template(job.jobtype.config_xml)
    context = get_context_for_template(job)
    # We need to strip leading/trailing whitespace in order to avoid having the
    # <?xml> PI not in the first line of the document.
    return template.render(context).strip()


def generate_job_name(jobtype):
    """
    Generates a "unique" id.
    """
    return "%s_%s" % (slugify(jobtype.name), timezone.now().strftime("%s"))


class DefaultSettings(object):
    """
    Allows easy configuration of default values for a Django settings.

    e.g. values = DefaultSettings({"NOTIFICATION_HOST": "http://example.com"})
    values.NOTIFICATION_HOST # returns the value from the default django
        settings, or the default if not provided in the settings.
    """
    class _defaults(object):
        pass

    def __init__(self, defaults):
        self.defaults = self._defaults()
        for key, value in defaults.iteritems():
            setattr(self.defaults, key, value)

    def __getattr__(self, key):
        return getattr(settings, key, getattr(self.defaults, key))

    def get_value_or_none(self, key):
        """
        Doesn't raise an AttributeError in the event that the key doesn't
        exist.
        """
        return getattr(settings, key, getattr(self.defaults, key, None))
