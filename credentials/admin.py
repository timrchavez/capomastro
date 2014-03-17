from django.contrib import admin

from credentials.models import SshKeyPair


admin.site.register(SshKeyPair)
