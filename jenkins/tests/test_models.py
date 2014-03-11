from django.test import TestCase

from jenkins.models import Build
from .factories import BuildFactory


class BuildTest(TestCase):

    def test_instantiation(self):
        """We can create Builds."""

    def test_ordering(self):
        """Builds should be ordered in reverse build order by default."""
        builds = BuildFactory.create_batch(5)
        build_numbers = sorted([x.number for x in builds], reverse=True)

        self.assertEqual(
            build_numbers,
            list(Build.objects.all().values_list("id", flat=True)))
