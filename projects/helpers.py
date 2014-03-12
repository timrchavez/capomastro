from django.conf import settings


class DefaultSettings(object):
    """
    Allows easy configuration of default values for a Django settings.

    e.g. settings = DefaultSettings({"NOTIFICATION_HOST": "http://example.com"})
    settings.NOTIFICATION_HOST # returns the value from the default django
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
        Doesn't raise an AttributeError in the event that the key doesn't exist.
        """
        return getattr(settings, key, getattr(self.defaults, key, None))
