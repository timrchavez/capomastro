from datetime import timedelta

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.template import Template, Context
from django.utils import timezone

from jenkins.models import Job, Build, Artifact
from jenkins.utils import get_notifications_url
from projects.helpers import DefaultSettings


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


class DependencyType(models.Model):
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


class Dependency(models.Model):

    name = models.CharField(max_length=255, unique=True)
    dependency_type = models.ForeignKey(DependencyType)
    job = models.ForeignKey(Job, null=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "dependencies"

    def __str__(self):
        return self.name

    def get_current_build(self):
        """
        Return the most recent build
        """
        if self.job is not None:
            finished_builds = self.job.build_set.filter(phase="FINISHED")
            if finished_builds.count() > 0:
                return finished_builds.order_by("-number")[0]


class ProjectDependency(models.Model):
    """
    Represents the build of a dependency used by a project.

    e.g. Project X can use build 20 of dependency Y while
         Project Z is using build 23.

         So, this is the specific "tag" version of the 
         dependency that's used by this project.

         We can have a UI that shows what the current version is
         and the current version, and allow promoting to a newer version.
    """
    dependency = models.ForeignKey(Dependency)
    project = models.ForeignKey("Project")
    auto_track = models.BooleanField(default=True)
    current_build = models.ForeignKey(Build, null=True)


class Project(models.Model):

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    dependencies = models.ManyToManyField(Dependency, through=ProjectDependency)

    def get_current_artifacts(self):
        """
        Returns a QuerySet of Artifact objects representing the Artifacts
        associated with the project dependencies at their current dependency
        level.
        """
        current_builds = []
        for dependency in ProjectDependency.objects.filter(project=self):
            current_builds.append(dependency.current_build)
        return Artifact.objects.filter(build__in=current_builds)

    def __str__(self):
        return self.name


class ProjectBuild(models.Model):
    """Represents a requested build of a Project."""

    project = models.ForeignKey(Project)
    requested_by = models.ForeignKey(User, null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=10, default="INCOMPLETE")
    build_id = models.CharField(max_length=20)

    def __str__(self):
        return self.project.name

    def get_current_artifacts(self):
        """
        Returns a QuerySet of Artifact objects representing the Artifacts
        associated with the builds of the project dependencies for this
        project build.
        """
        return Artifact.objects.filter(build__build_id=self.build_id)

    def save(self, **kwargs):
        if not self.pk:
            self.build_id = generate_projectbuild_id(self)
        super(ProjectBuild, self).save(**kwargs)


def generate_projectbuild_id(projectbuild):
    """
    Generates a daily-unique id for a given project.

    # TODO: Should this drop the ".0" when there's no previous builds?
    """
    # This is a possible race condition
    today = timezone.now()
    filters = {"requested_at__gt": today.replace(hour=0, minute=0, second=0),
               "requested_at__lte": today.replace(hour=23, minute=59, second=59),
               "project": projectbuild.project}
    today_count = ProjectBuild.objects.filter(**filters).count()
    return today.strftime("%%Y%%m%%d.%d" % today_count)



@receiver(post_save, sender=Build, dispatch_uid="new_build_handler")
def handle_new_build(sender, created, instance, **kwargs):
    if instance.job.dependency_set.exists():
        for dependency in instance.job.dependency_set.all():
            for project_dependency in dependency.projectdependency_set.filter(
                auto_track=True):
                project_dependency.current_build = instance
                project_dependency.save()
