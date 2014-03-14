from jenkins.tasks import build_job


def build_project(project, user=None):
    """
    Given a build, schedule building each of its dependencies.
    """
    from projects.models import ProjectBuild
    build = ProjectBuild.objects.create(
        project=project, requested_by=user)

    for dependency in project.dependencies.all():
        build_job.delay(dependency.job.pk, build.build_id)
    return build
