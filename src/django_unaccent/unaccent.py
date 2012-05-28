# coding: utf-8
"""Main file of unaccent, provide the monkey_patch_where_node() function that will monkey patch the django ORM
adding all operators present in the UnaccentOperation class (operators and smart_operators).
"""


from itertools import izip, repeat
import unicodedata

from django.db.models.sql import Query
from django.db.models.sql.where import WhereNode

original_where_node_add = WhereNode.add
monkey_patched = False


def patched_wherenode_add(self, data, connector):
    """Override the original WhereNode.add.

    On node insertion (this method) introspects the provided data object.
    If it's a list (Django uses lists exclusively in its internal), checks its lookup_type (eg: 'icontains', etc.).
    If its lookup_type match those of unaccent (eg: 'iunaccent'), inserts our own UnaccentNode that can render itself
    properly on sql query construction time.

    Args:
        data: tuple(Constraint, lookup_type, value) or a custom Node object we won't deal with
        connector: WhereNode.AND or WhereNode.OR
    """

    # Mimics WhereNode.add method, introspects the object about to be added to the WhereNode tree,
    # possibly applying relevant modifications which will eventually be passed to the orignal WhereNode.add method
    if isinstance(data, (list, tuple)):
        constraint, lookup_type, value = data

        # Introspect and shortcut with our special object if that match the UnaccentOperation keys
        accept, new_lookup_type = UnaccentOperation.accept(lookup_type, value)
        if accept:
            data = UnaccentNode(constraint.alias, constraint.col, constraint.field, new_lookup_type, value)
        else:
            data = (constraint, new_lookup_type, value)

    return original_where_node_add(self, data, connector)

def monkey_patch_where_node():

    global monkey_patched
    if monkey_patched is True:
        return
    monkey_patched = True

    # Update the operators accepted by a query when adding filters by adding those of unaccent
    # This way, it passes the test at db/models/sql/query.py:1021 which otherwise will override our custom lookup_types
    Query.query_terms.update(izip(UnaccentOperation.operators.keys() + UnaccentOperation.smart_operators, repeat(None)))
    WhereNode.add = patched_wherenode_add


class UnaccentNode(object):
    """Custom unaccent node object to be inserted in the WhereNode that can render sql by itself.
    """
    # As Constraint class, it could implement __setstate__ and __getstate__.

    def __init__(self, alias, col, field, lookup_type, value):
        self.table_alias = alias
        self.col_name = col
        self.field = field
        self.lookup_type = lookup_type
        self.value = value

    def sql_for_columns(self, qn, connection):
        """Taken from WhereNode.sql_for_columns"""

        db_type = self.field.db_type(connection=connection)

        if self.table_alias:
            lhs = '%s.%s' % (qn(self.table_alias), qn(self.col_name))
        else:
            lhs = qn(self.col_name)
        return connection.ops.field_cast_sql(db_type) % lhs

    def as_sql(self, qn, connection):
        """Having a as_sql method will short circuit the complex creation of make_atom in WhereNode

        Returns:
            tuple (query_part, query_params):
                querypart: string with place holder to insert each `query_param'
                query_params: list of params to insert in `query_part' that will be escaped properly
        """
        lookup_type, value = self.lookup_type, self.value

        field_sql_name = self.sql_for_columns(qn, connection)
        field_sql = UnaccentOperation.lookup_cast(lookup_type) % field_sql_name

        search_term = UnaccentOperation.get_db_prep_lookup(connection, lookup_type, value)

        query_part = '%s %s' % (field_sql, UnaccentOperation.operators[lookup_type])
        return query_part, (search_term,)

    def relabel_aliases(self, change_map):
        if self.alias in change_map:
            self.alias = change_map[self.alias]

class UnaccentOperation:

    operators = {
        'unaccent': '= unaccent(%s)',
        'iunaccent': '= UPPER(unaccent(%s))',
        'contains_unaccent': "LIKE unaccent(%s)",
        'icontains_unaccent': "LIKE UPPER(unaccent(%s))",
        'startswith_unaccent': "LIKE unaccent(%s)",
        'istartswith_unaccent': "LIKE UPPER(unaccent(%s))",
        'endswith_unaccent': "LIKE unaccent(%s)",
        'iendswith_unaccent': "LIKE UPPER(unaccent(%s))",
    }

    # Add smart operators, whose name are suffixed by _smart
    smart_operators = [op + '_smart' for op in operators]

    # Used by smart operators when accents are found in the search term
    non_unaccent_filter_fallback = {
        'unaccent': 'exact',
        'iunaccent': 'iexact',
        'contains_unaccent': 'contains',
        'icontains_unaccent': 'icontains',
        'startswith_unaccent': 'startswith',
        'istartswith_unaccent': 'istartswith',
        'endswith_unaccent': 'endswith',
        'iendswith_unaccent': 'iendswith',
    }

    @classmethod
    def accept(cls, lookup_type, search_term):
        """
        Returns:
            tuple (accepted, lookup_type):
                accepted: whether this lookup_type/search_time should receive special 'unaccent' treatment
                new_lookup_type: will differs from the original lookup_type if it was a smart lookup_type,
                                removes the '_smart' suffix or returns an equivalent 'non-unaccent' lookup_type
        """

        if lookup_type not in UnaccentOperation.operators and lookup_type not in UnaccentOperation.smart_operators:
            return False, lookup_type

        if lookup_type.endswith('_smart'):
            lookup_type = lookup_type[:-len('_smart')]

            if asciify(search_term) != search_term:
                # Some non-ascii char are used (accents), act as we were specifically looking for them
                # Don't unaccent and fallback to use an equivalent 'non-unaccen' lookup_type
                return False, cls.non_unaccent_filter_fallback[lookup_type]

        return True, lookup_type

    @classmethod
    def get_db_prep_lookup(cls, connection, lookup_type, value):
        """
        Returns:
            value: string, given the lookup_type, the identical value or a value processed for an incoming LIKE query
        """
        if lookup_type in ('contains_unaccent', 'icontains_unaccent'):
            return u"%{0}%".format(connection.ops.prep_for_like_query(value))

        if lookup_type in ('startswith_unaccent', 'istartswith_unaccent'):
            return u"{0}%".format(connection.ops.prep_for_like_query(value))

        if lookup_type in ('endswith_unaccent', 'iendswith_unaccent'):
            return u"%{0}".format(connection.ops.prep_for_like_query(value))

        return value

    @classmethod
    def lookup_cast(cls, lookup_type):
        """Build the left part of the query (the one related to the column)"""
        lookup = 'unaccent(%s::text)'

        # Use UPPER(x) for case-insensitive lookups; it's faster.
        if lookup_type in ('iunaccent', 'icontains_unaccent', 'istartswith_unaccent', 'iendswith_unaccent'):
            lookup = 'UPPER(%s)' % lookup

        return lookup


def asciify(unistr):
    """Returns an ascii string converting accented chars to normal ones.
    Unconvertible chars are just removed.

    Thanks at the Autolib' team for providing me this nice little helper!

    >>> asciify(u'Ééüçñøà')
        Eeucna
    """
    return unicodedata.normalize('NFKD', unicode(unistr)).encode('ascii', 'ignore')

