from __future__ import unicode_literals
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from jenkins.management.helpers import import_jenkinsserver


class Command(BaseCommand):
    help = "Import or update a JenkinsServer"
    args = "[name] [url] [username] [password] [remote]"

    option_list = BaseCommand.option_list + (
        make_option(
            "--update", action="store_true", dest="update",
            default=False, help="Update if server already exists."),
    )

    def handle(self, *args, **options):
        if len(args) != 5:
            raise CommandError("must provide all parameters")
        name, url, username, password, remote = args

        import_jenkinsserver(
           update=options["update"], stdout=self.stdout)

        transaction.commit_unless_managed()
