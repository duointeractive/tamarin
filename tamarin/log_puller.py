import boto
from boto.exception import S3ResponseError
from django.conf import settings
from tamarin.models import S3LoggedBucket, S3LogRecord
from tamarin.parser import S3LogParser

def store_parsed_entry(parsed):
    try:
        record = S3LogRecord.objects.get(request_id=parsed['request_id'])
    except S3LogRecord.DoesNotExist:
        record = S3LogRecord()

    manual_fields = ['id', 'bucket']
    fields = [field.name for field in record._meta.fields \
                if field.name not in manual_fields]
    for field in fields:
        setattr(record, field, parsed.get(field))

    record.bucket = S3LoggedBucket.objects.get(name=parsed['bucket'])

    record.save()

def pull_and_parse_logs():
    purge_parsed_keys = getattr(settings, 'TAMARIN_PURGE_PARSED_KEYS', False)
    logged_buckets = S3LoggedBucket.objects.get_log_buckets_to_monitor()
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                           settings.AWS_SECRET_ACCESS_KEY)

    for logged_bucket in logged_buckets:
        bucket = conn.get_bucket(logged_bucket.log_bucket_name)
        for key in bucket.get_all_keys():
            print key

            try:
                log_contents = key.get_contents_as_string()
            except S3ResponseError:
                # We're going to get a response error from time to time, S3
                # is not bullet proof. In this case, move on to the next
                # key and a later execution of the puller will grab this one.
                print "S3ResponseError encountered when retrieving: %s" % key
                continue

            parser = S3LogParser(log_contents)
            for log_entry in parser.parse_lines():
                store_parsed_entry(log_entry)

            if purge_parsed_keys:
                # Delete the key after parsing it if the
                # TAMARIN_PURGE_PARSED_KEYS setting is True. 
                key.delete()
