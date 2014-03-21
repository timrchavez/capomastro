#!/usr/bin/env python
import os
import sys


# This bootstraps the virtualenv so that the system Python can use it
app_root = os.path.dirname(os.path.realpath(__file__))
activate_this = os.path.join(app_root, 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "capomastro.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
