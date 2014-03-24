from django.core.management.base import CommandError
from requests.exceptions import HTTPError

from jenkins.models import JobType


REQUIRED_PLUGINS = ["notification"]


def verify_jenkinsserver(server):
    """
    Perform some perfunctory tests to check if a server is suitable for use
    with Capomastro.
    """
    messages = []
    try:
        client = server.get_client()
    except HTTPError as e:
        messages.append("ERROR: %s" % str(e))
    else:
        plugins = client.get_plugins()
        missing_plugins = []
        for plugin in REQUIRED_PLUGINS:
            if not plugin in plugins:
                missing_plugins.append(plugin)
        if missing_plugins:
            messages.append("Missing plugins: " + ",".join(missing_plugins))
    return messages


def import_jobtype(jobfile, job_name, update=False, stdout=None):
    """
    Import or update content to the specified job_name.
    """
    content = jobfile.read()
    try:
        job_type = JobType.objects.get(name=job_name)
        if update:
            job_type.config_xml = content
            job_type.save()
            if stdout:
                stdout.write("Job type updated")
        else:
            raise CommandError("Job type already exists")
    except JobType.DoesNotExist:
        JobType.objects.create(name=job_name, config_xml=content)
        if stdout:
            stdout.write("Job type created")
