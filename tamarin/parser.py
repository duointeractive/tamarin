"""
S3 log file parser, using PyParsing. The S3LogParser is instantiated with
the full string contents of a log key, and delegates the parsing of each line
to the S3LogLineParser class.

The primary user of this module is the `log_puller` module.
"""
import logging
import datetime
from dateutil import zoneinfo
from pyparsing import alphas, nums, alphanums, Combine, Word, Group, delimitedList, Suppress
from django.conf import settings

LOGGER = logging.getLogger(__name__)

class S3LogLineParser(object):
    """
    Parses individual lines within an S3 bucket log. Spits out 
    S3LogRecord objects.
    """
    FIELDS = (
        'bucket', 'request_dtime', 'remote_ip', 'requester',
        'request_id', 'operation', 'key', 'request_method',
        'request_uri', 'http_version', 'http_status', 'error_code',
        'bytes_sent', 'object_size', 'total_time', 'turnaround_time',
        'referrer', 'user_agent', 'version_id',
    )

    def __init__(self, line_contents):
        """
        :param str line_contents: The individual line/log entry to parse, in
            string form.
        """
        self.line_contents = line_contents

    def parse_line(self):
        """
        Parses the line that the S3LogLineParser class was instantiated with.
        
        :rtype: pyparsing.ParseResults
        :returns: A pyparsing ParseResults instance, which can be used much
            like a dict.
        """
        LOGGER.debug("-- RAW --" * 5)
        LOGGER.debug(self.line_contents)
        LOGGER.debug("-- RESULTS --" * 5)
        results = self.parse()
        LOGGER.debug(self._parse_result_debug_msg(results))
        return results

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
            like a dict.
        """
        # Some generic parsing patterns.
        integer = Word(nums)
        generic_alphanum = Word(alphanums)
        alpha_or_dash = Word(alphas + "-")
        num_or_dash = Word(nums + '-')

        # S3 bucket key name. Restrictions apply.
        bucket_str = Word(alphanums + '-_.')
        # IE: +400 or -400
        time_zone_offset = Word("+-", nums)
        # Abbreviated month: Jan, Feb, etc.
        month = Word(alphas, exact=3)
        # [04/Aug/2006:22:34:02 +0000]
        server_dtime = Group(
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
        # 72.21.206.5
        ip_address = delimitedList(integer, ".", combine=True)
        # 314159b66967d86f031c7249d1d9a80 or -
        requester = Word(alphanums + "-")
        # IE: SOAP.CreateBucket or REST.PUT.OBJECT
        operation = Word(alphas + "._")
        # S3 key: /photos/2006/08/puppy.jpg
        key = Word(alphanums + "/-_.?=%&:+<>#~[]")
        # One of GET, POST, or PUT
        http_method = Word(alphas)
        # HTTP/1.1
        http_protocol = Word(alphanums + "/.")

        # "GET /mybucket/photos/2006/08/ HTTP/1.1"
        uri = Suppress('"') + \
              http_method('request_method') + \
              key("request_uri") + \
              http_protocol('http_version') + \
              Suppress('"')
        dash_or_uri = ("-" | uri)

        # "http://www.amazon.com/webservices"
        referrer_uri = Suppress('"') + key + Suppress('"')
        # Referrer can be empty double quotes sometimes.
        empty_dquotes = Suppress('"') + Suppress('"')
        # Either a referrer, a dash, or empty double quotes.
        referrer_or_dash = referrer_uri | "-" | empty_dquotes

        # "curl/7.15.1"
        user_agent = Suppress('"') + \
                     Word(alphanums + "/-_.?=%&:(); ,+$@!^<>~[]'{}#*`") + \
                     Suppress('"')
        # User agent field can either be a user agent string or a dash.
        user_agent_or_dash = user_agent | "-" | empty_dquotes

        # The string value for each field below is what you refer to when
        # accessing the parsed values.
        log_line_bnf = (
            generic_alphanum("bucket_owner") +
            bucket_str("bucket") +
            server_dtime("request_dtime").setParseAction(self._action_dtime_parse) +
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

    def _parse_result_debug_msg(self, parsed):
        """
        Used to show useful output during debugging. Shows all of the parsed
        fields and their values.
        
        :param pyparsing.ParseResults parsed: A parsed log line.
        :rtype: str
        :return: A debug message that may be sent through the logger.
        """
        retval = ""
        for field in self.FIELDS:
            retval += "%s: %s\n" % (field, parsed.get(field, ''))
        return retval

class S3LogParser(object):
    """
    Handles the parsing of S3 bucket log key contents.
    """
    def __init__(self, log_contents):
        """
        :param str log_contents: The contents of the log file, in string form.
        """
        self.log_contents = log_contents

    def parse_lines(self):
        """
        Breaks the file up into lines and delegates the parsing of each
        line to :class:`S3LogLineParser`.
        
        :rtype: pyparsing.ParseResults
        :returns: A pyparsing ParseResults instance, which can be used much
            like a dict.
        """
        lines = self.log_contents.split('\n')
        for line in lines:
            if not line:
                # Empty line, skip.
                continue
            # Delegate to the line parser.
            line_parser = S3LogLineParser(line)
            # Return the pyparsing.ParseResults for the line.
            yield line_parser.parse_line()
