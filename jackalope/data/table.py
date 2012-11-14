"""

    table
    -----

    TODO FIXME XXX: sometimes key refers to a list of column names, and other
    times it refers to a dict of column/value pairs. is there a better term? is
    this clear enough that we dont have to worry about it?


"""

from util.decorators import constant
from jackalope.errors import OverrideRequiredError, AlreadySetError


class _Table(object):

    @constant
    def NAME(self):
        raise OverrideRequiredError()

    @constant
    def COLUMNS(self):
        raise OverrideRequiredError()

    @constant
    def PRIMARY_KEY(self):
        raise OverrideRequiredError()

    @constant
    def UNIQUE_KEYS(self):
        raise OverrideRequiredError()

    @constant
    def FOREIGN_KEYS(self):
        raise OverrideRequiredError()


class Table(object):


    def __init__(self, name, columns, primary_key, cursor=None):
        self._name = name
        self._columns = columns
        self._set_primary_key(primary_key)

        # TODO: find the right place to disallow access to the cursor until we
        # are sure that this field has been set.
        self._uses_auto_key = None


        # this doesn't strictly have to be required, but it is required here
        # for now. subclasses don't require it
        self._cursor = cursor


    @property
    def cursor(self):
        if not self._cursor:
            raise OverrideRequiredError()

        return self._cursor


    def _set_cursor(self, cursor):
        """Mutator for when subclass constructors don't require cursor."""
        self._cursor = cursor


    def _use_auto_key(self, uses_auto_key):
        self._uses_auto_key = uses_auto_key


    def _set_primary_key(self, key):
        # make this final once set
        if self._primary_key:
            raise AlreadySetError()

        # all tables need a primary key
        if not key:
            raise OverrideRequiredError()

        # sorting is guaranteed to enable comparisons throughout the class
        key.sort()

        self._primary_key = key


    def _set_unique_keys(self, keys):
        """Not required. Member won't exist unless invoked by a subclass."""
        # make this final once set
        if self._unique_keys:
            raise AlreadySetError()

        self._unique_keys = self._prepare_keys(keys)


    def _set_foreign_keys(self, keys):
        """Not required. Member won't exist unless invoked by a subclass."""
        # make this final once set
        if self._foreign_keys:
            raise AlreadySetError()

        self._foreign_keys = self._prepare_keys(keys)


    def _prepare_keys(self, keys):
        """Convenience helper for _set_*_keys methods."""
        # sorting is guaranteed to enable comparisons throughout the class
        for key in keys:
            key.sort()

        # ensure no overlap with the primary key
        if self._primary_key in keys:
            keys.remove(self._primary_key)

        return keys


    def _has_primary_key(self, properties):
        return set(self._primary_key).issubset(set(properties.keys()))


    def _in_columns(self, properties):
        return set(properties.keys()).issubset(set(self._columns))


    def _is_primary_key(self, key):
        """Is the given key the primary key? This isn't that useful."""
        return self._in_keys(key, [self._primary_key])


    def _is_unique_key(self, key):
        """Is the given key a unique key?"""
        return self._in_keys(key, self._unique_keys)


    def _is_foreign_key(self, key):
        """Is the given key a foreign key?"""
        return self._in_keys(key, self._foreign_keys)


    def _in_keys(self, key, keys):
        """Convenience helper for _is_*_key methods."""
        # sorting required for comparison
        key.sort()
        return key in keys


    def _create_row(self, properties):
        # properties shouldn't include the primary key if it's an auto-key
        if self._uses_auto_key:
            if self._has_primary_key(properties):
                # TODO: maybe make this error more helpful?
                raise KeyError()
        # but properties has to include the primary key if it's not an auto-key
        else:
            if not self._has_primary_key(properties):
                # TODO: maybe make this error more helpful?
                raise KeyError()

        # are the columns to insert real?
        if not self._in_columns(properties):
            # TODO: maybe make this error more helpful?
            raise KeyError()

        # TODO: make this an atomic action to ensure no one intervenes to mess
        # up the unordered properties dict, unwittingly mismatching the pairs.
        columns = properties.keys()
        parameters = properties.values()
        placeholders = ["%s" for i in range(len(parameters))]

        # TODO: add RETURNING <pk1, pk2, ...>?
        sql = "INSERT INTO {} ({}) VALUES ({})".format(
                self._name,
                ", ".join(columns),
                ", ".join(placeholders))

        return self._query_one(sql, parameters)


    def _create_or_update_row(self, unique_key, properties):
        # INSERT ... ON DUPLICATE KEY UPDATE
        raise NotImplementedError()


    def _read_row(self, unique_key):
        (condition, parameters) = self._all_equal(unique_key)

        sql = "SELECT {} FROM {} WHERE {}".format(
                ", ".join(self._columns),
                self._name,
                condition)

        return self._query_one(sql, parameters)


    def _read_rows_by_index(self, index):
        raise NotImplementedError()


    def _update_row(self, unique_key, properties):
        # are the columns to insert real?
        if not self._in_columns(properties):
            # TODO: maybe make this error more helpful?
            raise KeyError()

        # TODO FIXME XXX: make sure this doesn't screw up properties
        if self._has_primary_key(properties):
            for column in unique_key.keys():
                properties.pop(column)

        # TODO FIXME XXX: FILL ME IN WITH STUFF LIKE in _create_row!

        sql = "UPDATE {} SET {} WHERE {}".format(
                self._name,
                expressions,
                condition)

        # TODO FIXME XXX: be sure to carefully construct the parameters in
        # order since this will be the concatenation of two lists.

        return self._query_one(sql, parameters)


    def _delete_row(self, unique_key):
        raise NotImplementedError()


    def _query_one(self, sql, parameters):
        self._cursor.execute(sql, parameters)
        # TODO FIXME XXX: work on this! why the zero-indexing?
        return self._cursor.fetchone()[0]


    def _query_many(self, sql, parameters):
        self._cursor.execute(sql, parameters)
        # TODO FIXME XXX: work on this!
        return self._cursor.fetchmany()


    def _all_equal(self, properties):
        return self._condition(properties, "AND", "=")


    def _any_equal(self, properties):
        return self._condition(properties, "OR", "=")


    def _all_not_equal(self, properties):
        return self._condition(properties, "AND", "!=")


    def _any_not_equal(self, properties):
        return self._condition(properties, "OR", "!=")


    def _condition(self, properties, operator, comparator):
        # TODO: make this an atomic action to ensure no one intervenes to mess
        # up the unordered properties dict, unwittingly mismatching the pairs.
        columns = properties.keys()
        parameters = properties.values()

        # " AND " or " OR "
        operator_string = " {} ".format(operator.strip())

        # ["x=%s", "y=%s", "z=%s",]
        expressions = [
                "{}{}{}".format(column, comparator.strip(), "%s")
                for column in columns
                ]

        # "x=%s AND y=%s AND z=%s"
        condition = operator_string.join(expressions)

        return (condition, parameters,)
