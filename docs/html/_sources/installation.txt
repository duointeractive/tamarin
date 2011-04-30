.. _installation:

.. include:: global.txt

Installation
============

Tamarin is installed much like most Django apps.

Requirements
------------

* Python_ 2.5, 2.6, or 2.7
* Django_ >=1.2
* Boto_ >= 1.9b
* pyparsing_ >= 1.4

Obtaining the package
---------------------

You may install Tamarin via the :command:`easy_install` or :command:`pip`::

    easy_install tamarin

or::

    pip install tamarin
  
    
.. note::
    If you don't have access to :command:`pip`, you may download a tarball/zip, 
    from our `GitHub project`_ and install via the enclosed ``setup.py``.

Integration
-----------

You'll then want to add `tamarin` to your `INSTALLED_APPS`::

    INSTALLED_APPS = (
        ...
        'tamarin',
    )
    
After this, if you are using South_::

    ./manage.py migrate
    
If you are not using South_, you'll want to::

    ./manage syncdb
    
Setting up the log puller
-------------------------

The module that actually does the pulling of your S3 access logs is called
the log puller. There are currently two different ways to retrieve access
logs automatically:

* A celery_ task that fires at configurable intervals.
* A management command, ``tamarin_pull_logs``.

If you are already using celery_, you should be all set. You can adjust the
interval at which logs are pulled using the 
``TAMARIN_CELERY_PULL_PARSE_INTERVAL`` setting in settings.py. This is an
integer value (in minutes) for how often to check S3 for new logs.

If you don't have/want celery_, you may set up a cron entry to run
something like the following::

    ./manage.py tamarin_pull_logs
    
Set up bucket logging on S3
---------------------------

Before progressing any further, take a moment to set up bucket logging for
one or more of your buckets. You may point more than one bucket at the
same log bucket, but log buckets must only contain log files.

If you need details on how to do this, check out S3's `bucket logging`_
documentation.

.. warning:: If any files other than S3 access logs make their way into one
    of your log buckets, you will see errors, and the log puller will most
    likely not function.

.. _bucket logging: http://docs.amazonwebservices.com/AmazonS3/latest/dev/ServerLogs.html
    
Add buckets to monitor
----------------------

At this point, you should have installed Tamarin and configured your choice
of puller (celery or Django management command).

Log into your admin site, navigate to the Tamarin section. Add a 'S3 logged
bucket'.

.. tip::
    The ``name`` field is the bucket that the media resides in, not the name
    of its log bucket.
    
The ``Monitor bucket`` checkbox should default to being checked, but make
sure it is if you want this bucket to be pulled/parsed.

Profit
------

Once a bucket is added, your puller should take care of the rest. Note that
if you have a large backlog of logs to pull, this might take a good long
while, and may take multiple calls to the puller.

For an overview of what models and fields are available for querying,
see the :doc:`model_reference` page.