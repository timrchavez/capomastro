from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from jenkins.models import Job, Build


class DependencyType(models.Model):

    name = models.CharField(max_length=255)
    config_xml = models.TextField()

    def __str__(self):
        return self.name


class Dependency(models.Model):

    name = models.CharField(max_length=255)
    dependency_type = models.OneToOneField(DependencyType)
    job = models.ForeignKey(Job, editable=False, null=True)

    class Meta:
        verbose_name_plural = "dependencies"

    def __str__(self):
        return self.name


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


@receiver(post_save, sender=Build, dispatch_uid="new_build_handler")
def handle_new_build(sender, created, instance, **kwargs):
    if instance.job.dependency_set.exists():
        for dependency in instance.job.dependency_set.all():
            for project_dependency in dependency.projectdependency_set.filter(
                auto_track=True):
                project_dependency.current_build = instance
                project_dependency.save()
