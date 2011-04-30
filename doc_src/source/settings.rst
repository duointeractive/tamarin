.. settings:

.. include:: global.txt

Settings
========

Tamarin only has a few settings to tweak with in your :file:`settings.py`.

TAMARIN_CELERY_PULL_PARSE_INTERVAL
----------------------------------

*Default:* ``5``

This is an interval (in minutes) that determines how often to poll S3 for
new access logs. You'll want to bump this up past the default of *5 minutes*
if you have more than a handful of buckets to monitor.

.. note:: This setting is only used if you are running celery_.

TAMARIN_PURGE_PARSED_KEYS
-------------------------

*Default:* ``True``

When ``True``, keys are removed from your S3 access log buckets after being
successfully parsed. This will keep down the size of future requests, and
avoid re-parsing logs that we have already seen.