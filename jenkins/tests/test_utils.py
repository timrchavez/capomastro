from django.test import SimpleTestCase
from django.test.utils import override_settings

from jenkins.utils import (
    get_notifications_url, DefaultSettings, get_job_xml_for_upload,
    get_context_for_template)
from .factories import JobFactory, JobTypeFactory


class NotificationUrlTest(SimpleTestCase):

    def test_get_notifications_url(self):
        """
        get_notifications_url should reverse the notification url and return a
        complete HTTP URL from the base provided.
        """
        self.assertEqual(
            "http://example.com/jenkins/notifications/",
            get_notifications_url("http://example.com/"))


class DefaultSettingsTest(SimpleTestCase):

    def test_default_values(self):
        """
        Anything we put in the configuration is available as a property on the
        settings object.
        """
        settings = DefaultSettings({"SERVER_HOST": "testing"})
        self.assertEqual("testing", settings.SERVER_HOST)

    def test_missing_value(self):
        """
        We should get an attribute error if there is no setting for a value.
        """
        settings = DefaultSettings({})
        with self.assertRaises(AttributeError) as cm:
            settings.MY_UNKNOWN_VALUE

        self.assertEqual(
            "'_defaults' object has no attribute 'MY_UNKNOWN_VALUE'",
            str(cm.exception))

    def test_get_value_or_none(self):
        """
        DefaultSettings.get_value_or_none should return None if there is no
        value or if it's None.
        """
        settings = DefaultSettings({"MY_VALUE": None})

        self.assertIsNone(settings.get_value_or_none("MY_TEST_VALUE"))
        self.assertIsNone(settings.get_value_or_none("MY_VALUE"))


class GetContextForTemplate(SimpleTestCase):

    def test_get_context_for_template(self):
        """
        get_context_for_template should return a Context object with details
        from the job and anywhere else to be used when templating the job
        config.xml.
        """
        job = JobFactory.create()
        context = get_context_for_template(job)

        self.assertEqual(job, context.get("job"))
        self.assertEqual(
            "http://localhost/jenkins/notifications/",
            context.get("notifications_url"))


template_config = """
<?xml version='1.0' encoding='UTF-8'?>
<project>
  <actions/>
  <description>{{ jobtype.description }}</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <com.tikal.hudson.plugins.notification.HudsonNotificationProperty plugin="notification@1.5">
      <endpoints>
        <com.tikal.hudson.plugins.notification.Endpoint>
          <protocol>HTTP</protocol>
          <format>JSON</format>
          <url>{{ notifications_url }}</url>
        </com.tikal.hudson.plugins.notification.Endpoint>
      </endpoints>
    </com.tikal.hudson.plugins.notification.HudsonNotificationProperty>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.TextParameterDefinition>
          <name>BUILD_ID</name>
          <description></description>
          <defaultValue></defaultValue>
        </hudson.model.TextParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
</project>
"""


class GetTemplatedJobTest(SimpleTestCase):

    @override_settings(NOTIFICATION_HOST="http://example.com")
    def test_get_job_xml_for_upload(self):
        """
        get_job_xml_for_upload should take a job and return the XML that needs
        to be uploaded to build the job.
        """
        jobtype = JobTypeFactory.create(config_xml=template_config)
        job = JobFactory.create(jobtype=jobtype)
        xml_for_upload = get_job_xml_for_upload(job)
        expected_url = get_notifications_url("http://example.com/")
        self.assertIn(job.jobtype.description, xml_for_upload)
        self.assertIn(expected_url, xml_for_upload)
