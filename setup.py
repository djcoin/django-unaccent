#!/usr/bin/env python
# coding: utf-8

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
        name = "django-unaccent",
        version = "0.1",
        author = "Simon Thépot aka djcoin",
        author_email = "simon.thepot@gmail.com",
        description = ("Integration of nice operators to the Django ORM for unaccented search in postgresql"),
        license = "BSD",
        keywords = "django postgres postgresql orm unaccent",
        # url = "",
        package_dir = {'': 'src'},
        packages = ['django_unaccent'],
        long_description=read('README.rst'),
        install_requires = [
            'django>=1.1,<1.4',
            # https://code.djangoproject.com/ticket/16250
            'psycopg2<=2.4.1',
        ],
        tests_require = [
        ],
        classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    test_suite='runtests',
)
