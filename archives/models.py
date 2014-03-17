from django.db import models
from .policies import CdimageArchivePolicy
from credentials.models import SshKeyPair
from .archivers import SshArchiver


POLICIES = {'cdimage': CdimageArchivePolicy}
TRANSPORTS = {'ssh': SshArchiver}


class Archive(models.Model):
    name = models.CharField(max_length=64)
    host = models.CharField(max_length=64)
    policy = models.CharField(
    	max_length=64, choices=[(p, p) for p in POLICIES.keys()])
    basedir = models.CharField(max_length=128)
    username = models.CharField(max_length=64)
    ssh_credentials = models.ForeignKey(SshKeyPair)
    transport = models.CharField(
    	max_length=64, choices=[(p, p) for p in TRANSPORTS.keys()])

    def __unicode__(self):
    	return self.name
