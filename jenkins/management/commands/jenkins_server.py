# from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction

from jenkins.models import JenkinsServer


def list_servers(stdout):
    servers = list(JenkinsServer.objects.all())
    if len(servers) > 0:
        max_name = max(len(s.name) for s in servers)
        max_url = max(len(s.url) for s in servers)
        format_string = "{:<%d}  {:<%d}\n" % (max_name, max_url)
        for server in servers:
            stdout.write(format_string.format(server.name, server.url))
    else:
        stdout.write("No servers")


class Command(BaseCommand):
    help = "Jenkins server management"

    # option_list = BaseCommand.option_list + (
    #     make_option(
    #         "-j", dest="job_id",
    #         help="Job Id to process"),)

    def handle(self, command, *args, **options):
        if command == 'list':
            list_servers(self.stdout)
        transaction.commit_unless_managed()
