.. _index:

.. include:: global.txt

==============================================
Tamarin: S3 access log parser/store for Django
==============================================

Tamarin is a drop-in Django_ app for parsing/storing S3_ access logs in a
Django model. This allows to build queries against your historic data.

.. note:: Tamarin provides no analysis tools besides a model that you may
    query. Analysis is best left to other apps that use the models provided
    here.

How it works
------------

Tamarin uses celery_ or a Django management command to list the keys in
log buckets that you specify. The contents of the keys are downloaded
and parsed using pyparsing_ and stored in a Django model. From there, it is
up to you to do what you'd like with the data.

No other functionality is included. It is up to you to analyze and use the
data for your specific case. However, if you write anything cool that uses
data from Tamarin, please open an issue on the `issue tracker`_ and we'll
link you here. 

Usage cases
-----------

Tamarin may be useful to you if you are interested in monitoring...

* Which IP addresses consume the most bandwidth.
* Files that are responsible for the biggest chunk of your bill.
* 404s.
* Referring sites.

You might also like Tamarin if you want to...

* Perform simple or complex analysis of your S3 access logs using Django's ORM.
* Implement automatic banning of bandwidth hogs (not included in app).
* Create pretty charts and graphs (in another app). 
* Set up bandwidth spike alarms.

Learning more
-------------

**Project Status:** Stable

**License:** Tamarin is licensed under the `BSD License`_.

These links may also be useful to you.

* Source repository: https://github.com/duointeractive/tamarin
* Issue tracker: https://github.com/duointeractive/tamarin/issues

Documentation
-------------

.. toctree::
   :maxdepth: 2
   
   installation
   settings
   model_reference

