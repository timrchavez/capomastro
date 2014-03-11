import logging

from jenkins.models import Job, Build, Artifact


def import_builds_for_job(job_id):
    """
    Import all Builds for a job using the job_id.

    stdout should be a writable object.
    """
    job = Job.objects.get(pk=job_id)

    logging.info("Located job %s\n" % job)

    client = job.server.get_client()

    logging.info("Using server at %s\n" % job.server.url)

    jenkins_job = client.get_job(job.name)

    good_build_ids = list(jenkins_job.get_build_ids())
    logging.info("%s\n" % good_build_ids)

    for build_id in good_build_ids:
        build_result = jenkins_job.get_build(build_id)
        # TODO: Shouldn't access _data here.
        build_details = {
            "job": job,
            "result": build_result.get_status(),
            "build_id": build_result._data["id"],
            "number": build_result.buildno,
            "duration": build_result._data["duration"],
            "url": build_result.get_result_url()
        }
        logging.info("%s" % build_details)
        build = Build.objects.create(**build_details)
        for artifact in build_result.get_artifacts():
            artifact_details = {
                "filename": artifact.filename,
                "url": artifact.url,
                "build": build
            }
            logging.info("%s" % artifact_details)
            Artifact.objects.create(**artifact_details)
