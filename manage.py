#!/usr/bin/env python
import os
import sys

STAGE = os.environ['STAGE']

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"backend.settings.{STAGE.lower()}")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
