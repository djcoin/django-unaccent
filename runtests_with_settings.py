#!/usr/bin/env python

import sys, os

from django.conf import settings

from django.test.simple import DjangoTestSuiteRunner
from django.utils import unittest


class UnaccentDjangoTestSuiteRunner(DjangoTestSuiteRunner):

    def setup_test_environment(self, **kwargs):
        super(UnaccentDjangoTestSuiteRunner, self).setup_test_environment(**kwargs)
        self.teardown_callbacks = []
        push_teardown_cb = self.teardown_callbacks.append

        restore_installed_apps =  getattr(settings, 'INSTALLED_APPS', None)
        push_teardown_cb(lambda: setattr(settings, 'INSTALLED_APPS', restore_installed_apps))

    def teardown_test_environment(self, **kwargs):
        super(UnaccentDjangoTestSuiteRunner, self).teardown_test_environment(**kwargs)
        [ f() for f in self.teardown_callbacks ]


    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        # Make django-unaccent searchable
        unaccent_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'django_unaccent')
        sys.path.insert(0, unaccent_dir)

        suite = unittest.TestSuite()

        from django_unaccent import tests
        suite.addTest(tests.suite())

        return suite



def runtests(verbosity=1, interactive=False, failfast=False, *test_args):
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()


    test_runner = UnaccentDjangoTestSuiteRunner(verbosity=verbosity, interactive=interactive, failfast=failfast)
    return test_runner.run_tests(test_labels=None, extra_tests=None)

