"""
Log file parser. 
"""
import datetime
import string
from pyparsing import alphas, nums, dblQuotedString, Combine, Word, Group, delimitedList, Suppress, removeQuotes
from tamarin.models import S3LogRecord, S3LoggedBucket

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
        :returns: The datetime.datetime equivalent of the time string.
        """
        # Comes in as [['22/Apr/2011:18:28:10', '+000']] but we're just
        # interested in the time, since strptime with a %z formatter doesn't
        # work as expected on all platforms.
        dtime_str = t[0][0]
        # 22/Apr/2011:18:28:10
        return datetime.datetime.strptime(dtime_str, "%d/%b/%Y:%H:%M:%S")

    def parse(self):
        """
        Parses the class's :attr:`line_contents` attribute using pyparsing.
        
        :rtype: pyparsing.ParseResults
        :returns: A pyparsing ParseResults instance, which can be used much
            like a dict. the setResultsName method is used to determine the
            name of the key on the ParseResults object.
        """
        integer = Word(nums)
        generic_alphanum = Word(alphas + nums)
        alpha_or_dash = Word(alphas + "-")
        num_or_dash = Word(nums + '-')

        bucket_str = Word(alphas + nums + '-' + '_')

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

        requester = Word(alphas + nums + "-")

        operation = Word(alphas + "." + "_")

        key = Word(alphas + nums + "/" + "-" + "_" + "." + "?" + "="
                   + "%" + "&")

        http_method = Word(string.uppercase)

        http_protocol = Word(alphas + nums + "/" + ".")

        log_line_bnf = (
            generic_alphanum.setResultsName("bucket_owner") +
            bucket_str.setResultsName("bucket") +
            serverDateTime.setResultsName("request_dtime").setParseAction(self._action_dtime_parse) +
            ip_address.setResultsName("remote_ip") +
            requester.setResultsName("requester") +
            generic_alphanum.setResultsName("request_id") +
            operation.setResultsName("operation") +
            key.setResultsName("key") +
            Suppress("\"") +
            http_method.setResultsName("request_method") +
            key.setResultsName("request_uri") +
            http_protocol.setResultsName("http_version") +
            Suppress("\"") +
            integer.setResultsName('http_status') +
            alpha_or_dash.setResultsName('error_code') +
            num_or_dash.setResultsName('bytes_sent') +
            num_or_dash.setResultsName('object_size') +
            integer.setResultsName('total_time') +
            num_or_dash.setResultsName('turnaround_time') +
            dblQuotedString.setResultsName('referrer').setParseAction(removeQuotes) +
            dblQuotedString.setResultsName('user_agent').setParseAction(removeQuotes) +
            alpha_or_dash.setResultsName('version_id')
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
        print "request_method:", parsed['request_method']
        print "request_uri:", parsed['request_uri']
        print "http_version:", parsed['http_version']
        print "http_status:", parsed['http_status']
        print "error_code:", parsed['error_code']
        print "bytes_sent:", parsed['bytes_sent']
        print "object_size:", parsed['object_size']
        print "total_time:", parsed['total_time']
        print "turnaround_time:", parsed['turnaround_time']
        print "referrer:", parsed['referrer']
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
            setattr(record, field, parsed[field])

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
            if not line or "REST.GET.OBJECT" not in line:
                continue
            line_parser = S3LogLineParser(line)
            line_parser.parse_and_store()
