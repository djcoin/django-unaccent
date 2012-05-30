Django-Unaccent
=================

.. image:: https://secure.travis-ci.org/djcoin/django-unaccent.png?branch=master
    :target: http://travis-ci.org/djcoin/django-unaccent/


Add unaccent search to the Django ORM like a breeze !
This currently only works for the *Postgres database* but contribution are welcome
to push it to other databases or to extend its features !


Operator's list
---------------

This library add new operators to the django ORM by a clean (!) monkey patch.
These operator's name share the same name as the existing operators provided by
the Django ORM, only suffixed by '_unaccent'.
Here is the exhaustive list of new operators available:

- *unaccent*: unaccented search
- *iunaccent*: unaccented case insensitive search
- *contains_unaccent*: unaccented contains
- *icontains_unaccent*: unaccented case insensitive contains
- *startswith_unaccent*: unaccented prefix search
- *istartswith_unaccent*:  unaccented case insensitive prefix search
- *endswith_unaccent*: unaccented suffix search
- *iendswith_unaccent*: unaccented case insensitive suffix search


To this list we can add the "smart" version of each of those operators,
eg: *unaccent_smart* or *iendswith_unaccent_smart* ('_smart' suffix!).
The smart unaccent version will not make an unaccent search if an accent is specified
and will fall back to a classic (exact) search.
This can come in handy if you do not want to be bothered by results that do not match accent when any is provided.


Example
-------

::

    $ ./manage.py shell
    >>> from django.contrib.auth.models import User
    >>> User.objects.all().delete()
    >>> User.objects.create(username=u"Ôtâèkù")
    >>> User.objects.filter(name__icontains_unaccent='tae') # Here we go !
    <User: Ôtâèkù>

Check out the tests for even more examples !

Database set up for unaccented search
=====================================

PostgreSQL
----------

Important note: it seems recent versions of PostgreSQL (> 8.4) have the unaccent extension provided by default.
We did not investigate this yet. What matters however is that your database can make unaccented search
when the *unaccent* function is triggered in SQL (eg: select * from mytable where mycolumn = unaccent('Tchüs');).

This was tested with the 8.4 version of PostgreSQL on a debian-like distribution.
Install the ``unaccent`` extension (see the .travis.yml file for the setup script)::

    $ apt-get install postgresql-server-dev-8.4 libunac1 libunac1-dev
    $ cd /tmp
    $ wget "http://launchpad.net/postgresql-unaccent/trunk/0.1/+download/postgresql-unaccent-0.1.tar.gz"
    $ tar -zxvf postgresql-unaccent-0.1.tar.gz
    $ cd postgresql-unaccent-0.1
    $ make && sudo make install

The extension is now installed and can be added to any existing bases or templates::

    $ psql -d template1 -f $(pg_config --sharedir)/contrib/unaccent.sql

Quick test::

    $ psql template1 -c 'select unaccent('éèàù');'
    eeau


Testing
=======

Tests are provided in the tests.py file.
To test the library, get the sources and run::

    $ python runtests.py

Database default Django's options are::

    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django_unaccent_db',
        'USER': 'django_unaccent_user',
        'PASSWORD': '',
        'HOST': '',
    }

You can modify those options when running runtests.py::

    python runtests.py -d my_db -u my_user -p my_password


**Note**: *python setup.py test* is not provided as it should be used for immediate test after install.
Our set up is too tedious (get and cmmi unaccent, make the database) to match this goal.


The requirements are:

* The django_unaccent_table exists and has the the unaccent sql function available (see Database set up section)
* The user who will the run test  must have the right to create database (needed by Django test mechanism)
  You can create one with::

    psql -d postgres -c "create user django_unaccent_user with createdb password 'django_unaccent_password'"
    createdb -T template1 django_unaccent_table -O django_unaccent_user


See: http://www.postgresql.org/docs/8.4/static/auth-pg-hba-conf.html


Performance
===========

The library will apply the *unaccent* postgres function to the search input and to each field of
the column you are querying against (note that this also happens every time you make a case insensitive search !).
While this may never be a problem, we know (no benchmark yet!) this is not quite optimized and may start
to be costly if you have millions of rows !

Postgres
--------

To enhance performance, you may one or several index on common queried fields
(see http://www.postgresql.org/docs/8.4/static/sql-createindex.html for more information) like so::

    CREATE INDEX username_idx ON films ((unaccent(title)));

If you have any optimization tricks, let us know !

TODO
====

* Ensure compatibility with recent postgres database unaccent feature
* Push new database compatibility (MySQL, etc.) ?
* Enhance running of test as a standalone lib but also as a lib included in a Django project
  (I'm struggling as this is a "standalone" lib with no urlconf/settings - Django is not a great fan of this -
  + the unaccent function is needed to perform those tests)

Author
======

Simon Thépot.

I am looking for a new maintainer and will be glad to give commit rights to any serious forthcoming maintainer :)

