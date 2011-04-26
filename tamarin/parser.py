"""
Log file parser. 
"""
from pprint import pprint

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
        print(self.line_contents)
        pprint(self.parse())

    def parse(self):
        tokens = self.line_contents.split()
        print tokens

        request_dtime_str = tokens[2] + tokens[3]

        return {
            "bucket_owner": tokens[0],
            "bucket": tokens[1],
            "request_dtime": request_dtime_str,
            "remote_ip": tokens[4],
            "requester": tokens[5],
            "request_id": tokens[6],
            "operation": tokens[7],
            "key": tokens[8],
            "request_method": tokens[9],
            "request_uri": tokens[10],
            "http_version": tokens[11],
            "http_status": tokens[12],
            "error_code": tokens[13],
            "bytes_sent": tokens[14],
            "object_size": tokens[15],
            "total_time": tokens[16],
            "turnaround_time": tokens[17],
            "referrer": tokens[18],
            "user_agent": ' '.join(tokens[19:-2]),
            "version_id": tokens[-1],
        }

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
            line_parser = S3LogLineParser(line)
            line_parser.parse_and_store()
            break
