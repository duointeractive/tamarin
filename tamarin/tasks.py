import datetime
from django.conf import settings
from celery.task import PeriodicTask
from tamarin.log_puller import pull_and_parse_logs

class PullAndParseS3Logs(PeriodicTask):
    """
    Pulls and parses S3 bucket logs at intervals. The
    TAMARIN_CELERY_PULL_PARSE_INTERVAL setting is used to determine the
    firing interval for this task. This number should decrease towards one
    minute as more buckets are monitored to prevent backlog.
    """
    pull_interval = getattr(settings, 'TAMARIN_CELERY_PULL_PARSE_INTERVAL', 5)
    run_every = datetime.timedelta(minutes=pull_interval)

    def run(self, **kwargs):
        """
        Do the same thing that the tamarin_pull_logs management command does.
        """
        pull_and_parse_logs()

