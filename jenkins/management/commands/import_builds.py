from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from jenkins.helpers import import_builds_for_job


class Command(BaseCommand):
    help = "Jenkins build importer"

    option_list = BaseCommand.option_list + (
        make_option(
            "-j", dest="job_id",
            help="Job Id to process"),)

    def handle(self, *args, **options):
        import_builds_for_job(int(options['job_id']))
        transaction.commit_unless_managed()
