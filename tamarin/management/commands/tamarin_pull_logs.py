"""
The tamarin_pull_logs management command may be used in conjunction with
cron or another task scheduler if you don't have or want to use celery.
"""
from django.core.management.base import BaseCommand
from tamarin.log_puller import pull_and_parse_logs

class Command(BaseCommand):
    """
    Nothing magical here, just using the log puller.
    """
    help = "Looks through S3 logs for broadcast media to find the hogs."

    def handle(self, *args, **options):
        """
        Call the log pulling function and do work silently.
        """
        pull_and_parse_logs()
