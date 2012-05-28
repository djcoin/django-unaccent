#!/usr/bin/env python

from collections import namedtuple
import sys, os
from optparse import OptionParser, make_option

from django.conf import settings


# the table need to have the unaccent sql function available
# The user must have the right to create a table
DbConnectionInfo = namedtuple('DbConnectionInfo', ['name', 'user', 'password', 'host'])

default_db_connection_info = DbConnectionInfo(
  name='django_unaccent_db',
  user='django_unaccent_user',
  password='django_unaccent_password',
  host='',
)

def get_minimal_django_settings(db_info=default_db_connection_info):
    return dict(
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': db_info.name,
                'USER': db_info.user,
                'PASSWORD': db_info.password,
                'HOST': db_info.host,
            }
        },
    )


def set_settings_and_runtests(db_connection_info, verbosity=1, interactive=False, failfast=False):
    if not settings.configured:
        settings.configure(**get_minimal_django_settings(db_connection_info))

    ### Importing DjangoTestSuiteRunner makes Django fails with an import error on 'signals' ###
    ### The real reason is that the settings, found or not, are not initialized ###
    from runtests_with_settings import runtests
    return_code = runtests()

    sys.exit(return_code)



if __name__ == '__main__':
    opt_db_info = default_db_connection_info

    opt_list = [
            # Database settings
            make_option('-d', '--database', default=opt_db_info.name,
                help='The database to use for testing django-unaccent. Must have the unaccent SQL function available'),
            make_option('-u', '--user', default=opt_db_info.user,
                help='Django test user to connect to the database, must have creation of database right.'),
            make_option('-p', '--password', default=opt_db_info.password,
                help='password, if any, to connect to the database'),
            make_option('-H', '--host', default=opt_db_info.host, help=''),
            # Add test settings ?
            # parser.add_option('--failfast', action='store_true', default=False, dest='failfast')
    ]

    parser = OptionParser(option_list=opt_list)

    options, _ = parser.parse_args()

    db_info = DbConnectionInfo(options.database, options.user, options.password, options.host)

    set_settings_and_runtests(db_info)


