"""
Tamarin is a Django app for retrieving, parsing, and storing S3 logs.

Interesting bits are in models.py (Django model definitions), log_puller.py
(the functions used to set all of the pieces in motion), and parser.py (the
PyParsing-based log parser). The rest are just your typical support modules
seen in most Django apps.
"""
# Major, minor.
VERSION = (1, 2)
