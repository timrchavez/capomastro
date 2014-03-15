from jenkins.tasks import build_job


def build_project(project, user=None, dependencies=None, queue_build=True):
    """
    Given a build, schedule building each of its dependencies.
    """
    dependencies = dependencies and dependencies or []
    if dependencies:
        filter_args = {"pk__in": [x.pk for x in dependencies]}
    else:
        filter_args = {}

    from projects.models import ProjectBuild, ProjectBuildDependency
    build = ProjectBuild.objects.create(
        project=project, requested_by=user)

    for dependency in project.dependencies.filter(**filter_args):
        ProjectBuildDependency.objects.create(
            projectbuild=build,
            dependency=dependency)
        if queue_build:
            build_job.delay(dependency.job.pk, build.build_id)
    return build
