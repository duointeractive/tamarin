"""
This module is used to put all of the pieces together and provide a single
point of entry to get logs pulled, parsed, and stored. The only important
function in this module for users is :func:`pull_and_parse_logs`. This is what
the celery task and the Django management command (tamarin_pull_logs) call
to get things going.
"""
import logging
import boto
from boto.exception import S3ResponseError
from django.conf import settings
from tamarin.models import S3LoggedBucket, S3LogRecord
from tamarin.parser import S3LogParser

# The following fields should not be pulled from the parser's results. They
# are either set when the model is saved (id), or in store_parsed_entry.
MANUAL_FIELDS = ['id', 'bucket']
# Logger for this module.
LOGGER = logging.getLogger(__name__)

def store_parsed_entry(parsed):
    """
    Given a parsed log entry, copy the values from the parser's output to
    a S3LogRecord object. If the log already exists, update the values.
    
    :param pyparsing.ParseResults parsed: The parsed results for a single
        log entry.
    :rtype: S3LogRecord
    :returns: The updated or newly created S3LogRecord object for the
        parsed log entry.
    """
    try:
        record = S3LogRecord.objects.get(request_id=parsed['request_id'])
    except S3LogRecord.DoesNotExist:
        record = S3LogRecord()

    field_names = [field.name for field in record._meta.fields \
                      if field.name not in MANUAL_FIELDS]
    for field in field_names:
        setattr(record, field, parsed.get(field))

    record.bucket = S3LoggedBucket.objects.get(name=parsed['bucket'])
    record.save()
    return record

def pull_and_parse_logs():
    """
    Pulls all of the keys from the bucket's log bucket, hands them off to the
    parser, then stores the values in S3LogRecord objects.
    """
    # When True, delete S3 log keys after they have been parsed.
    purge_parsed_keys = getattr(settings, 'TAMARIN_PURGE_PARSED_KEYS', True)
    # All buckets with monitor_bucket == True (active).
    logged_buckets = S3LoggedBucket.objects.get_log_buckets_to_monitor()
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                           settings.AWS_SECRET_ACCESS_KEY)

    for logged_bucket in logged_buckets:
        bucket = conn.get_bucket(logged_bucket.log_bucket_name)
        for key in bucket.get_all_keys():
            LOGGER.debug(key)

            try:
                # Stuff the entire contents of the S3 key into string variable.
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
