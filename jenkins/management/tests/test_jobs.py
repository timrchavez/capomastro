from __future__ import unicode_literals

from cStringIO import StringIO

from django.core.management.base import CommandError
from django.test import TestCase

from jenkins.management.helpers import import_jobtype
from jenkins.models import JobType


class ImportJobTest(TestCase):

    def test_import_job_creates_a_jobtype(self):
        """
        import_jobtype should create a jobtype with the correct name and
        content.
        """
        stdout = StringIO()
        import_jobtype("my test", StringIO("my test"), stdout=stdout)

        job = JobType.objects.get(name="my test")
        self.assertEqual("my test", job.config_xml)
        self.assertEqual("Job type created\n", stdout.getvalue())

    def test_import_job_fails_with_preexisting_jobtype(self):
        """
        import_jobtype should error if we already have a jobtype with the
        supplied name.
        """
        JobType.objects.create(name="my test", config_xml="testing")
        with self.assertRaises(CommandError) as cm:
            import_jobtype("my test", StringIO("new content"))

        self.assertEqual("Job type already exists", str(cm.exception))
        job = JobType.objects.get(name="my test")
        self.assertEqual("testing", job.config_xml)

    def test_import_job_updates_a_jobtype(self):
        """
        import_jobtype should update the content if we provide a true value for
        the update parameter.
        """
        stdout = StringIO()
        JobType.objects.create(name="my test", config_xml="testing")
        import_jobtype(
            "my test", StringIO("new content"), update=True, stdout=stdout)

        job = JobType.objects.get(name="my test")
        self.assertEqual("new content", job.config_xml)
        self.assertEqual("Job type updated\n", stdout.getvalue())
