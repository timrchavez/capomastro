import logging

from jenkins.models import Job, Build, Artifact
from jenkins.utils import generate_job_name


def import_build_for_job(job_pk, build_number):
    """
    Import a build for a job.
    """
    job = Job.objects.get(pk=job_pk)
    logging.info("Located job %s\n" % job)

    client = job.server.get_client()
    logging.info("Using server at %s\n" % job.server.url)

    jenkins_job = client.get_job(job.name)
    build_result = jenkins_job.get_build(build_number)

    # TODO: Shouldn't access _data here.
    build_details = {
        "status": build_result.get_status(),
        # TODO: What should we do with this ID we get from Jenkins?
        # Discard? or only set it if we don't have one?
        # "build_id": build_result._data["id"],
        "duration": build_result._data["duration"],
        "url": build_result.get_result_url(),
        "console_log": build_result.get_console_log(),
    }
    logging.info("%s" % build_details)
    Build.objects.filter(job=job, number=build_number).update(**build_details)
    build = Build.objects.get(job=job, number=build_number)
    for artifact in build_result.get_artifacts():
        artifact_details = {
            "filename": artifact.filename,
            "url": artifact.url,
            "build": build
        }
        logging.info("%s" % artifact_details)
        Artifact.objects.create(**artifact_details)


def create_job(jobtype, server):
    """
    Create a job in the given Jenkins Server.
    """
    name = generate_job_name(jobtype)
    job = Job.objects.create(jobtype=jobtype, server=server, name=name)
    return job


def import_builds_for_job(job_pk):
    """
    Import all Builds for a job using the job_pk.

    TODO: Add testing - only used by command-line tool just now.
    """
    job = Job.objects.get(pk=job_pk)

    logging.info("Located job %s\n" % job)

    client = job.server.get_client()

    logging.info("Using server at %s\n" % job.server.url)

    jenkins_job = client.get_job(job.name)

    good_build_numbers = list(jenkins_job.get_build_ids())
    logging.info("%s\n" % good_build_numbers)

    for build_number in good_build_numbers:
        import_build_for_job(job.pk, build_number)
