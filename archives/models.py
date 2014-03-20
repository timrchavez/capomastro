from django.db import models

from credentials.models import SshKeyPair
from archives.policies import CdimageArchivePolicy
from archives.archivers import SshArchiver


POLICIES = {"cdimage": CdimageArchivePolicy}
ARCHIVERS = {"ssh": SshArchiver}


class Archive(models.Model):

    name = models.CharField(max_length=64)
    host = models.CharField(max_length=64)
    policy = models.CharField(
        max_length=64, choices=[(p, p) for p in POLICIES.keys()])
    basedir = models.CharField(max_length=128)
    username = models.CharField(max_length=64)
    ssh_credentials = models.ForeignKey(SshKeyPair)
    transport = models.CharField(
        max_length=64, choices=[(p, p) for p in ARCHIVERS.keys()])

    def __str__(self):
        return self.name

    def get_policy(self):
        """
        Returns a class to be used as the archive name generation policy for
        this archive or None.
        """
        return POLICIES.get(self.policy)

    def get_archiver(self):
        """
        Returns a class to be used to archive files for this archive or None.
        """
        return ARCHIVERS.get(self.transport)
