# vim: set fileencoding=utf-8 :

from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase
from django.utils import unittest


from .unaccent import monkey_patch_where_node


monkey_patch_where_node()


class UnaccentTestCase(TestCase):

    def setUp(self):
        self.nomatch = u"ZZZ"

        self.username = u"Ôtâèkù"
        self.ascii_username = u"Otaeku"

        self.user = User(username=self.username)
        self.user.save()

    def swap_username(self, start=0, end=None):
        """Transform the slice from start to end of username in its ascii counterpart.
        Defaut parameters implies the complete ascii_username to be returned.
        """
        end = end if end is not None else len(self.ascii_username)
        return self.username[:start] + self.ascii_username[start:end] + self.username[end:]

    def assert_match(self, *args, **kwargs):
        self.assertTrue(User.objects.filter(*args, **kwargs).exists())
        # Additional test with the Q syntax
        self.assertTrue(User.objects.filter(Q(*args, **kwargs)).exists())

    def assert_no_match(self, *args, **kwargs):
        self.assertFalse(User.objects.filter(*args, **kwargs).exists())
        # Additional test with the Q syntax
        self.assertFalse(User.objects.filter(Q(*args, **kwargs)).exists())

    def test_unaccent(self):

        for filtr in ('username__unaccent', 'username__unaccent_smart'):
            self.assert_match((filtr, self.username))
            self.assert_match((filtr, self.ascii_username))
            self.assert_no_match((filtr, self.username[1:]))
            self.assert_no_match((filtr, self.username[:-1]))

        username_with_missing_accent = u"Ôtaèkù"
        self.assert_match(('username__unaccent', username_with_missing_accent))
        self.assert_no_match(('username__unaccent_smart', username_with_missing_accent))

    def test_iunaccent(self):

        for filtr in ('username__iunaccent', 'username__iunaccent_smart'):
            self.assert_match((filtr, self.username))
            self.assert_match((filtr, self.ascii_username))
            self.assert_match((filtr, self.username.lower()))
            self.assert_match((filtr, self.username.upper()))
            self.assert_match((filtr, self.ascii_username.lower()))
            self.assert_match((filtr, self.ascii_username.upper()))
            self.assert_no_match((filtr, self.username[1:]))
            self.assert_no_match((filtr, self.username[:-1]))

        username_with_missing_accent = u"Ôtaèkù".upper()
        self.assert_match(('username__iunaccent', username_with_missing_accent))
        self.assert_no_match(('username__iunaccent_smart', username_with_missing_accent))

    def test_contains_unaccent(self):

        for filtr in ('username__contains_unaccent', 'username__contains_unaccent_smart'):
            self.assert_match((filtr, self.username[1:-1]))
            self.assert_match((filtr, self.ascii_username[1:-1]))
            self.assert_no_match((filtr, self.nomatch))

        username_with_missing_accent = u"Ôtaèkù"[1:-1]
        self.assert_match(('username__contains_unaccent', username_with_missing_accent))
        self.assert_no_match(('username__contains_unaccent_smart', username_with_missing_accent))

    def test_icontains_unaccent(self):

        for filtr in ('username__icontains_unaccent', 'username__icontains_unaccent_smart'):
            self.assert_match((filtr, self.username[1:-1]))
            self.assert_match((filtr, self.ascii_username[1:-1]))
            self.assert_match((filtr, self.username[1:-1].lower()))
            self.assert_match((filtr, self.ascii_username[1:-1].lower()))
            self.assert_match((filtr, self.username[1:-1].upper()))
            self.assert_match((filtr, self.ascii_username[1:-1].upper()))
            self.assert_no_match((filtr, self.nomatch))

        username_with_missing_accent = u"Ôtaèkù"[1:-1].upper()
        self.assert_match(('username__icontains_unaccent', username_with_missing_accent))
        self.assert_no_match(('username__icontains_unaccent_smart', username_with_missing_accent))

    def test_startswith_unaccent(self):

        for filtr in ('username__startswith_unaccent', 'username__startswith_unaccent_smart'):
            self.assert_match((filtr, self.username[:-1]))
            self.assert_match((filtr, self.ascii_username[:-1]))
            self.assert_no_match((filtr, self.username[1:]))
            self.assert_no_match((filtr, self.ascii_username[1:]))

        username_with_missing_accent = u"Ôtaèkù"[:-1]
        self.assert_match(('username__startswith_unaccent', username_with_missing_accent))
        self.assert_no_match(('username__startswith_unaccent_smart', username_with_missing_accent))

    def test_istartswith_unaccent(self):

        for filtr in ('username__istartswith_unaccent', 'username__istartswith_unaccent_smart'):
            self.assert_match((filtr, self.username[:-1]))
            self.assert_match((filtr, self.ascii_username[:-1]))
            self.assert_match((filtr, self.username[:-1].lower()))
            self.assert_match((filtr, self.ascii_username[:-1].lower()))
            self.assert_match((filtr, self.username[:-1].upper()))
            self.assert_match((filtr, self.ascii_username[:-1].upper()))
            self.assert_no_match((filtr, self.username[1:]))
            self.assert_no_match((filtr, self.ascii_username[1:]))

        username_with_missing_accent = u"Ôtaèkù"[:-1].upper()
        self.assert_match(('username__istartswith_unaccent', username_with_missing_accent))
        self.assert_no_match(('username__istartswith_unaccent_smart', username_with_missing_accent))

    def test_endswith_unaccent(self):

        for filtr in ('username__endswith_unaccent', 'username__endswith_unaccent_smart'):
            self.assert_match((filtr, self.username[1:]))
            self.assert_match((filtr, self.ascii_username[1:]))
            self.assert_no_match((filtr, self.username[:-1]))
            self.assert_no_match((filtr, self.ascii_username[:-1]))

        username_with_missing_accent = u"Ôtaèkù"[1:]
        self.assert_match(('username__endswith_unaccent', username_with_missing_accent))
        self.assert_no_match(('username__endswith_unaccent_smart', username_with_missing_accent))

    def test_iendswith_unaccent(self):

        for filtr in ('username__iendswith_unaccent', 'username__iendswith_unaccent_smart'):
            self.assert_match((filtr, self.username[1:]))
            self.assert_match((filtr, self.ascii_username[1:]))
            self.assert_match((filtr, self.username[1:].lower()))
            self.assert_match((filtr, self.ascii_username[1:].lower()))
            self.assert_match((filtr, self.username[1:].upper()))
            self.assert_match((filtr, self.ascii_username[1:].upper()))
            self.assert_no_match((filtr, self.username[:-1]))
            self.assert_no_match((filtr, self.ascii_username[:-1]))

        username_with_missing_accent = u"Ôtaèkù"[1:].upper()
        self.assert_match(('username__iendswith_unaccent', username_with_missing_accent))
        self.assert_no_match(('username__iendswith_unaccent_smart', username_with_missing_accent))


def suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(UnaccentTestCase))
    return s

