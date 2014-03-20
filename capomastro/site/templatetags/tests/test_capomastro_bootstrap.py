from django.core.urlresolvers import reverse
from django.template import Template, Context
from django.test.client import RequestFactory
from django.test import SimpleTestCase

from capomastro.site.templatetags.capomastro_bootstrap import (
    build_status_to_class, active_url)


class StatusToClass(SimpleTestCase):

    def test_build_status_to_class(self):
        """
        build_status_to_class should convert the status of a build "SUCCESS",
        "ABORTED" etc to a class suitable for Bootstrap tables.
        """
        for status, class_ in [
                ("SUCCESS", "success"), ("ABORTED", "info"),
                ("FAILURE", "danger"), ("", "")]:
            self.assertEqual(class_, build_status_to_class(status))

    def test_build_status_to_class_in_template(self):
        """
        The build_status_to_class filter translates a Jenkins build status to a
        Bootstrap table class.
        """
        template = Template("{% load capomastro_bootstrap %}"
                            "{{ build_status|build_status_to_class }}")
        rendered = template.render(Context({"build_status": "SUCCESS"}))
        self.assertEqual("success", rendered)


class ActiveUrlTest(SimpleTestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_active_url_with_matching_url(self):
        """
        active_url requires django.core.context_processors.request and returns
        "active" if the request url matches the passed-in named url.
        """
        request = self.factory.get(reverse("home"))
        context = {"request": request}
        self.assertEqual("active", active_url(context, "home"))

    def test_active_url_with_non_matching_url(self):
        """
        active_url requires django.core.context_processors.request and returns
        "active" if the request url matches the passed-in named url.
        """
        request = self.factory.get("/my/non-existent-url")
        context = {"request": request}
        self.assertEqual("", active_url(context, "home"))

    def test_active_url_in_template(self):
        """
        We should get the "active" result when appropriate.
        """
        request = self.factory.get(reverse("home"))
        context = {"request": request}
        template = Template("{% load capomastro_bootstrap %}"
                            "{% active_url 'home' %}")
        rendered = template.render(Context(context))
        self.assertEqual("active", rendered)
