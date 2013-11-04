import sys

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.cache import cache

class Command(BaseCommand):

    def handle(self, *args, **options):

        print "Flushing all memcached values."
        cache._cache.flush_all()

        print "Done."