from django.core.management.base import BaseCommand
from tamarin.log_puller import pull_and_parse_logs

class Command(BaseCommand):
    help = "Looks through S3 logs for broadcast media to find the hogs."

    host_freqs = {}
    file_freqs = {}

    def handle(self, *args, **options):
        pull_and_parse_logs()
