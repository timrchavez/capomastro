from django.core.management.base import BaseCommand
from django.db import transaction

from jenkins.models import JenkinsServer
from jenkins.management.helpers import verify_jenkinsserver


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


def verify_server(name, stdout):
    try:
        server = JenkinsServer.objects.get(name=name)
        messages = verify_jenkinsserver(server)
        if not messages:
            stdout.write("Server at %s verifies ok." % server.url)
        else:
            stdout.write("\n".join(messages))
    except JenkinsServer.DoesNotExist:
        stdout.write("Could not find server %s" % name)

class Command(BaseCommand):
    help = "Jenkins server management"

    # TODO: This needs a rework to make the commands available through the help
    # etc.
    def handle(self, command, *args, **options):
        if command == "list":
            list_servers(self.stdout)
        elif command == "verify":
            verify_server(args[0], self.stdout)
        transaction.commit_unless_managed()
