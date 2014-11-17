"""
Useful auxiliary data structures for query construction. Not useful outside
the SQL domain.
"""
from django.db.models.sql.constants import INNER, LOUTER


class EmptyResultSet(Exception):
    pass


class MultiJoin(Exception):
    """
    Used by join construction code to indicate the point at which a
    multi-valued join was attempted (if the caller wants to treat that
    exceptionally).
    """
    def __init__(self, names_pos, path_with_names):
        self.level = names_pos
        # The path travelled, this includes the path to the multijoin.
        self.names_with_path = path_with_names


class Empty(object):
    pass


class BaseTable(object):
    join_type = None

    def __init__(self, table_name, alias):
        self.table_name = table_name
        self.lhs_alias = alias

    def as_sql(self, compiler, connection):
        alias_str = '' if self.lhs_alias == self.table_name else (' %s' % self.lhs_alias)
        base_sql = compiler.quote_name_unless_alias(self.table_name)
        return base_sql + alias_str, []

    def relabeled_clone(self, change_map):
        return self.__class__(self.table_name, change_map.get(self.lhs_alias, self.lhs_alias))


class Join(object):
    def __init__(self, table_name, rhs_alias, lhs_alias, join_type,
                 join_cols, join_field, nullable):
        self.table_name = table_name
        # From alias
        self.rhs_alias = rhs_alias
        # To alias
        self.lhs_alias = lhs_alias
        # LOUTER or INNER
        self.join_type = join_type
        # A list of 2-tuples to use in the ON clause of the JOIN.
        # Each 2-tuple will create one join condition in the ON clause.
        self.join_cols = join_cols
        # Along which field (or RelatedObject in the reverse join case)
        self.join_field = join_field
        # Is this join nullabled?
        self.nullable = nullable

    def as_sql(self, compiler, connection):
        """
        Generates the full
           LEFT OUTER JOIN sometable ON sometable.somecol = othertable.othercol, params
        clause for this join.
        """
        params = []
        sql = []
        alias_str = '' if self.rhs_alias == self.table_name else (' %s' % self.rhs_alias)
        qn = compiler.quote_name_unless_alias
        qn2 = connection.ops.quote_name
        sql.append('%s %s%s ON ('
                   % (self.join_type, qn(self.table_name),
                      alias_str))
        for index, (lhs_col, rhs_col) in enumerate(self.join_cols):
            if index != 0:
                sql.append(' AND ')
            sql.append('%s.%s = %s.%s' %
                       (qn(self.lhs_alias), qn2(lhs_col), qn(self.rhs_alias), qn2(rhs_col)))
        extra_cond = self.join_field.get_extra_restriction(
            compiler.query.where_class, self.rhs_alias, self.lhs_alias)
        if extra_cond:
            extra_sql, extra_params = compiler.compile(extra_cond)
            extra_sql = 'AND (%s)' % extra_sql
            params.extend(extra_params)
            sql.append('%s' % extra_sql)
        sql.append(')')
        return ' '.join(sql), params

    def relabeled_clone(self, change_map):
        new_lhs_alias = change_map.get(self.lhs_alias, self.lhs_alias)
        new_rhs_alias = change_map.get(self.rhs_alias, self.rhs_alias)
        return self.__class__(
            self.table_name, new_rhs_alias, new_lhs_alias, self.join_type,
            self.join_cols, self.join_field, self.nullable)

    def demote(self):
        new = self.relabeled_clone({})
        new.join_type = INNER
        return new

    def promote(self):
        new = self.relabeled_clone({})
        new.join_type = LOUTER
        return new
