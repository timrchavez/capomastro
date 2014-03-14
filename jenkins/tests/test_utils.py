from django.test import SimpleTestCase

from jenkins.utils import get_notifications_url


class NotificationUrlTest(SimpleTestCase):

    def test_get_notifications_url(self):
        """
        get_notifications_url should reverse the notification url and return a
        complete HTTP URL from the base provided.
        """
        self.assertEqual(
            "http://example.com/jenkins/notifications/",
            get_notifications_url("http://example.com/"))
