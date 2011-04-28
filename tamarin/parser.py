"""
Log file parser. 
"""
import logging
import datetime
from dateutil import zoneinfo
import string
from pyparsing import alphas, nums, alphanums, dblQuotedString, Combine, Word, Group, delimitedList, Suppress, removeQuotes
from django.conf import settings

logger = logging.getLogger(__name__)

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
        :param str line_contents: The individual line/log entry to parse.
        """
        self.line_contents = line_contents

    def parse_line(self):
        logger.debug("-- RAW --" * 5)
        logger.debug(self.line_contents)
        logger.debug("-- RESULTS --" * 5)
        results = self.parse()
        logger.debug(self._parse_result_debug_msg(results))
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

    def _parse_result_debug_msg(self, parsed):
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
        :param str log_contents: The contents of the log file.
        """
        self.log_contents = log_contents

    def parse_lines(self):
        lines = self.log_contents.split('\n')
        for line in lines:
            if not line:
                continue
            line_parser = S3LogLineParser(line)
            yield line_parser.parse_line()
