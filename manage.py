#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    
    if os.path.exists('PRODUCTION'):    
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hopefullysunny.production")
        os.environ['DJANGO_SETTINGS_MODULE'] = 'hopefullysunny.production'
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hopefullysunny.settings")
        os.environ['DJANGO_SETTINGS_MODULE'] = 'hopefullysunny.development'

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
