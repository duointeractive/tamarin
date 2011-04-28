"""
Log file parser. 
"""
import datetime
from dateutil import zoneinfo
import string
from pyparsing import alphas, nums, alphanums, dblQuotedString, Combine, Word, Group, delimitedList, Suppress, removeQuotes
from tamarin.models import S3LogRecord, S3LoggedBucket
from django.conf import settings

class S3LogLineParser(object):
    """
    Parses individual lines within an S3 bucket log. Spits out 
    S3LogRecord objects.
    """
    def __init__(self, line_contents):
        """
        :param str line_contents: The individual line/log entry to parse.
        """
        self.line_contents = line_contents

    def parse_and_store(self):
        print "-- RAW --" * 5
        print(self.line_contents)
        print "-- RESULTS --" * 5
        results = self.parse()
        self._test_print(results)

        self.store(results)

    def _action_dtime_parse(self, full_str, length, t):
        """
        Parses an S3-formatted time string into a datetime.datetime instance.
        
        :param str full_str: The full, un-parsed time string.
        :param int length: The length of the text to parse.
        :param list t: The grouped string to parse.
        :rtype: datetime.datetime
        :returns: The datetime.datetime equivalent of the time string with
            the correct (settings.TIME_ZONE) timezone set.
        """
        # Comes in as [['22/Apr/2011:18:28:10', '+000']] but we're just
        # interested in the time, since strptime with a %z formatter doesn't
        # work as expected on all platforms.
        dtime_str = t[0][0]
        # 22/Apr/2011:18:28:10
        utc = datetime.datetime.strptime(dtime_str, "%d/%b/%Y:%H:%M:%S")
        # The parsed time is in UTC. Make it "aware".
        utc = utc.replace(tzinfo=zoneinfo.gettz('UTC'))
        if settings.TIME_ZONE != 'UTC':
            # Get the user's local timezone.
            to_zone = zoneinfo.gettz(settings.TIME_ZONE)
            # Set the timezone to the configured TZ.
            return utc.astimezone(to_zone)
        else:
            # Already UTC, don't budge.
            return utc

    def parse(self):
        """
        Parses the class's :attr:`line_contents` attribute using pyparsing.
        
        :rtype: pyparsing.ParseResults
        :returns: A pyparsing ParseResults instance, which can be used much
            like a dict. the setResultsName method is used to determine the
            name of the key on the ParseResults object.
        """
        integer = Word(nums)
        generic_alphanum = Word(alphanums)
        alpha_or_dash = Word(alphas + "-")
        num_or_dash = Word(nums + '-')

        bucket_str = Word(alphanums + '-_')

        time_zone_offset = Word("+-", nums)

        month = Word(string.uppercase, string.lowercase, exact=3)

        serverDateTime = Group(
                             Suppress("[") +
                             Combine(
                                 integer + "/" +
                                 month + "/" +
                                 integer + ":" +
                                 integer + ":" +
                                 integer + ":" +
                                 integer) +
                             time_zone_offset +
                             Suppress("]")
                         )

        ip_address = delimitedList(integer, ".", combine=True)

        requester = Word(alphanums + "-")

        operation = Word(alphas + "._")

        key = Word(alphanums + "/-_.?=%&:+<>#~[]")

        http_method = Word(string.uppercase)

        http_protocol = Word(alphanums + "/.")

        uri = Suppress('"') + \
              http_method('request_method') + \
              key("request_uri") + \
              http_protocol('http_version') + \
              Suppress('"')
        dash_or_uri = ("-" | uri)

        referrer_uri = Suppress('"') + key + Suppress('"')
        empty_dquotes = Suppress('"') + Suppress('"')
        referrer_or_dash = referrer_uri | "-" | empty_dquotes

        user_agent = Suppress('"') + Word(alphanums + "/-_.?=%&:(); ,+$@!^<>~[]'{}#*`") + Suppress('"')

        user_agent_or_dash = user_agent | "-"

        log_line_bnf = (
            generic_alphanum("bucket_owner") +
            bucket_str("bucket") +
            serverDateTime("request_dtime").setParseAction(self._action_dtime_parse) +
            ip_address("remote_ip") +
            requester("requester") +
            generic_alphanum("request_id") +
            operation("operation") +
            key("key") +
            dash_or_uri("request_uri") +
            integer('http_status') +
            alpha_or_dash('error_code') +
            num_or_dash('bytes_sent') +
            num_or_dash('object_size') +
            num_or_dash('total_time') +
            num_or_dash('turnaround_time') +
            referrer_or_dash('referrer') +
            user_agent_or_dash('user_agent') +
            alpha_or_dash('version_id')
        )
        return log_line_bnf.parseString(self.line_contents)

    def _test_print(self, parsed):
        print "bucket_owner:", parsed['bucket_owner']
        print "bucket:", parsed['bucket']
        print "request_dtime:", parsed['request_dtime']
        print "remote_ip:", parsed['remote_ip']
        print "requester:", parsed['requester']
        print "request_id:", parsed['request_id']
        print "operation:", parsed['operation']
        print "key:", parsed['key']
        print "request_method:", parsed.get('request_method', '')
        print "request_uri:", parsed.get('request_uri', '')
        print "http_version:", parsed.get('http_version', '')
        print "http_status:", parsed['http_status']
        print "error_code:", parsed['error_code']
        print "bytes_sent:", parsed['bytes_sent']
        print "object_size:", parsed['object_size']
        print "total_time:", parsed['total_time']
        print "turnaround_time:", parsed['turnaround_time']
        print "referrer:", parsed.get('referrer')
        print "user_agent:", parsed['user_agent']
        print "version_id:", parsed['version_id']

    def store(self, parsed):
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

class S3LogParser(object):
    """
    Handles the parsing of S3 bucket log key contents.
    """
    def __init__(self, log_contents):
        """
        :param str log_contents: The contents of the log file.
        """
        self.log_contents = log_contents

    def parse_and_store(self):
        lines = self.log_contents.split('\n')
        for line in lines:
            # XXX: Don't limit to REST.GET.OBJECT. Requires some
            # PyParsing magic that I don't understand yet.
            #if "REST.GET.OBJECT" not in line:
            #    continue
            if not line:
                continue
            line_parser = S3LogLineParser(line)
            line_parser.parse_and_store()
