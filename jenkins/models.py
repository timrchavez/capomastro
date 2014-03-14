from django.db import models

from jenkinsapi.jenkins import Jenkins


class JenkinsServer(models.Model):

    name = models.CharField(max_length=255, unique=True)
    url = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    remote_addr = models.CharField(max_length=255)

    def __str__(self):
        return "%s (%s)" % (self.name, self.url)

    def get_client(self):
        """
        Returns a configured jenkinsapi Jenkins client.
        """
        return Jenkins(
            self.url, username=self.username, password=self.password)


class Job(models.Model):

    server = models.ForeignKey(JenkinsServer)
    name = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Build(models.Model):

    job = models.ForeignKey(Job)
    build_id = models.CharField(max_length=255)
    number = models.IntegerField()
    duration = models.IntegerField(null=True)
    url = models.CharField(max_length=255)
    phase = models.CharField(max_length=25) # FINISHED, STARTED, COMPLETED
    status = models.CharField(max_length=255)

    class Meta:
        ordering = ["-number"]

    def __str__(self):
        return self.build_id


class Artifact(models.Model):

    build = models.ForeignKey(Build)
    filename = models.CharField(max_length=255)
    url = models.CharField(max_length=255)


def get_context_for_template(dependency):
    """
    Returns a Context for the Job XML templating.
    """
    settings = DefaultSettings({"NOTIFICATION_HOST": "http://localhost"})
    notifications_url = get_notifications_url(settings.NOTIFICATION_HOST)
    context_vars = {
        "notification_host": get_notifications_url(settings.NOTIFICATION_HOST),
        "dependency": dependency,
    }
    return Context(context_vars)


class JobType(models.Model):
    """
    Used as a model for creating new Jenkins jobs.
    """

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    config_xml = models.TextField()

    def __str__(self):
        return self.name

    def generate_config_for_dependency(self, dependency):
        """
        Parse the config XML as a Django template, replacing {{}} holders etc
        as appropriate.
        """
        context = get_context_for_template(dependency)
        return Template(self.config_xml).render(context)
