from datetime import timedelta

from django.template import Template, Context
from django.test import SimpleTestCase

from jenkins.templatetags.jenkins_tags import (
    build_time_to_timedelta)


class BuildTimeToTimeDeltaTest(SimpleTestCase):

    def test_build_time_to_timedelta(self):
        """
        build_time_to_timedelta should return a timedelta for the millseconds
        that the build took.
        """
        self.assertEqual(timedelta(milliseconds=331),
                         build_time_to_timedelta(331))

    def test_build_time_to_timedelta_with_no_time(self):
        """
        If the build time is None (hasn't completed) then we should get an
        empty string back.
        """
        self.assertEqual("", build_time_to_timedelta(None))

    def test_build_time_to_timedelta_in_template(self):
        """
        The build_time_to_timedelta filter translates a build time to a time
        period.
        """
        template = Template("{% load jenkins_tags %}"
                            "{{ 127692|build_time_to_timedelta }}")
        rendered = template.render(Context())
        self.assertEqual("0:02:07.692000", rendered)
