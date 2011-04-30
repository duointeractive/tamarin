Tamarin
=======

Tamarin is a Django app used for parsing storing S3 bucket log data in local
models. Said data can be used for monitoring:

* Resource usage for each bucket
* Which hosts are consuming the most buckets
* Which files are being downloaded most frequently

Tamarin's only purpose is to retrieve the logs from S3, parse them, and store
them locally in a Django model. You'll need to write your own queries and
reports, or use another third party app that builds on Tamarin.  

Status
------

Tamarin is not recommended for production use... yet.
  
Documentation
-------------

Docstring only at this point.
  
License
-------

Tamarin is licensed under the `BSD License`_.

.. _BSD License: https://github.com/duointeractive/tamarin/blob/master/LICENSE
