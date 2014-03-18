from django.db import models
from paramiko.rsakey import RSAKey
from StringIO import StringIO


class SshKeyPair(models.Model):
    """
    Only supports RSA keys at the moment.
    """
    label = models.CharField(max_length=128)
    public_key = models.TextField()
    private_key = models.TextField()

    def __unicode__(self):
        return self.label

    def get_pkey(self):
        """
        Returns an RSAKey for use with paramiko SSHClient.
        """
        return RSAKey(data=self.public_key, file_obj=StringIO(self.private_key))
