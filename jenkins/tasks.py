from celery.utils.log import get_task_logger
from celery import shared_task

from jenkins.helpers import import_build_for_job
from jenkins.models import Job

logger = get_task_logger(__name__)


@shared_task
def import_build_task(job_id, build_number):
    import_build_for_job(job_id, build_number)


@shared_task
def build_job(job_pk):
    """
    Request building Job.
    """
    job = Job.objects.get(pk=job_pk)
    client = job.server.get_client()

    client.build_job(job.name)
