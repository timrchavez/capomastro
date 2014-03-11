from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from jenkins.models import Job, Build, Artifact


class DependencyType(models.Model):

    name = models.CharField(max_length=255)
    config_xml = models.TextField()

    def __str__(self):
        return self.name


class Dependency(models.Model):

    name = models.CharField(max_length=255, unique=True)
    dependency_type = models.ForeignKey(DependencyType)
    job = models.ForeignKey(Job, null=True)

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

    name = models.CharField(max_length=255)
    dependencies = models.ManyToManyField(Dependency, through=ProjectDependency)

    def get_current_artifacts(self):
        """
        """
        current_builds = []
        for dependency in ProjectDependency.objects.filter(project=self):
            current_builds.append(dependency.current_build)
        return Artifact.objects.filter(build__in=current_builds)

    def __str__(self):
        return self.name


class ProjectBuild(models.Model):

    project = models.ForeignKey(Project)
    requested_by = models.ForeignKey(User)
    requested_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=10, default="INCOMPLETE")

    def __str__(self):
        return self.project.name


@receiver(post_save, sender=Build, dispatch_uid="new_build_handler")
def handle_new_build(sender, created, instance, **kwargs):
    if instance.job.dependency_set.exists():
        for dependency in instance.job.dependency_set.all():
            for project_dependency in dependency.projectdependency_set.filter(
                auto_track=True):
                project_dependency.current_build = instance
                project_dependency.save()
