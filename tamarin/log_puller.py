import boto
from django.conf import settings
from tamarin.models import S3LoggedBucket, S3LogRecord
from tamarin.parser import S3LogParser

def pull_and_parse_logs():
    logged_buckets = S3LoggedBucket.objects.get_log_buckets_to_monitor()
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                               settings.AWS_SECRET_ACCESS_KEY)
    for logged_bucket in logged_buckets:
        bucket = conn.get_bucket(logged_bucket.log_bucket_name)
        for key in bucket.get_all_keys():
            print key
            log_contents = key.get_contents_as_string()
            parser = S3LogParser(log_contents)
            parser.parse_and_store()
            break
