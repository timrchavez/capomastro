from celery.utils.log import get_task_logger
from celery import shared_task

from jenkins.helpers import import_build_for_job
from jenkins.models import Job

logger = get_task_logger(__name__)


@shared_task
def import_build_task(job_id, build_number):
    import_build_for_job(job_id, build_number)


@shared_task
def build_job(job_pk, build_id=None):
    """
    Request building Job.
    """
    # TODO: If a job is already queued, then this can throw
    # WillNotBuild: <jenkinsapi.job.Job job> is already queued
    # Should we check for it being queued? with is_queued_or_running?
    job = Job.objects.get(pk=job_pk)
    client = job.server.get_client()
    params = {}
    if build_id is not None:
        params["BUILD_ID"] = build_id
    client.build_job(job.name, params=params)
