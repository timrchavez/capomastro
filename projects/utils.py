from jenkins.models import Build
from projects.models import ProjectDependency


def get_recent_builds_for_dependency(dependency):
    """
    Get the most recent 5 builds for a given dependency.
    """
    return Build.objects.filter(job=dependency.job).order_by("-number")[:5]


def get_build_table_for_project(project):
    """
    Returns a table of dependencies

    """
    dependencies = list(ProjectDependency.objects.filter(project=project))

    recent_builds = {}
    current_builds = {}
    for project_dependency in dependencies:
        dependency = project_dependency.dependency
        recent_builds[dependency] = get_recent_builds_for_dependency(
            dependency)
        current_builds[dependency] = project_dependency.current_build

    build_table = []
    build_table.append([x.dependency for x in dependencies])
    for row in range(5):
        current_row = []
        for project_dependency in dependencies:
            dependency = project_dependency.dependency
            current_build = recent_builds[dependency][row]
            current_row.append(
                (current_build, current_builds[dependency] == current_build))
        build_table.append(current_row)
    return build_table
