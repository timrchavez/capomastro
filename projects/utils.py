from jenkins.models import Build
from projects.models import ProjectDependency


def get_recent_builds_for_dependency(dependency):
    """
    Get the most recent 5 builds for a given dependency.
    """
    return list(
        Build.objects.filter(job=dependency.job).order_by("-number")[:5])


def get_build_for_row(builds, row):
    try:
        return builds[row]
    except IndexError:
        return


def get_build_table_for_project(project):
    """
    Returns a tuple with header row, list of rows
    """
    dependencies = list(ProjectDependency.objects.filter(project=project))

    recent_builds = {}
    current_builds = {}
    for projectdependency in dependencies:
        dependency = projectdependency.dependency
        recent_builds[dependency] = get_recent_builds_for_dependency(
            dependency)
        current_builds[dependency] = projectdependency.current_build

    # Deal with possible extra builds outwith recent builds.
    rows_to_count = 5
    for projectdependency in dependencies:
        dependency = projectdependency.dependency
        if projectdependency.current_build not in recent_builds[dependency]:
            recent_builds[dependency].append(projectdependency.current_build)
            rows_to_count = 6

    header_row = [x.dependency for x in dependencies]
    build_rows = []
    for row in range(rows_to_count):
        current_row = []
        for projectdependency in dependencies:
            dependency = projectdependency.dependency
            current_build = get_build_for_row(recent_builds[dependency], row)
            current_row.append(
                {"build": current_build,
                 "current": current_builds[dependency] == current_build})
        build_rows.append(current_row)
    return header_row, build_rows
