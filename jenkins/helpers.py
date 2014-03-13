import logging

from jenkins.models import Job, Build, Artifact


def import_build_for_job(job_id, build_number):
    """
    Import a build for a job.
    """
    job = Job.objects.get(pk=job_id)
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
        "url": build_result.get_result_url()
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


#def import_builds_for_job(job_id):
#    """
#    Import all Builds for a job using the job_id.
#    """
#    job = Job.objects.get(pk=job_id)
#
#    logging.info("Located job %s\n" % job)
#
#    client = job.server.get_client()
#
#    logging.info("Using server at %s\n" % job.server.url)
#
#    jenkins_job = client.get_job(job.name)
#
#    good_build_ids = list(jenkins_job.get_build_ids())
#    logging.info("%s\n" % good_build_ids)
#
#    for build_id in good_build_ids:
#        build_result = jenkins_job.get_build(build_id)
#        # TODO: Shouldn't access _data here.
#        build_details = {
#            "job": job,
#            "status": build_result.get_status(),
#            "build_id": build_result._data["id"],
#            "number": build_result.buildno,
#            "duration": build_result._data["duration"],
#            "url": build_result.get_result_url()
#        }
#        logging.info("%s" % build_details)
#        build = Build.objects.create(**build_details)
#        for artifact in build_result.get_artifacts():
#            artifact_details = {
#                "filename": artifact.filename,
#                "url": artifact.url,
#                "build": build
#            }
#            logging.info("%s" % artifact_details)
#            Artifact.objects.create(**artifact_details)
