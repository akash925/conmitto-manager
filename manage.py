#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    if not os.environ.get('DJANGO_ENV') or os.environ.get('DJANGO_ENV') == 'development':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        print(sys.version)
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
            "Look above to be sure you're using Python3"
        )
    execute_from_command_line(sys.argv)
