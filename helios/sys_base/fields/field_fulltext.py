# -*- coding: utf-8 -*-

from sys_util.text.query import parse_fts_query

from django.db import models
from django.db.models import Lookup
from django.db.models.aggregates import Aggregate
from django.db.models.fields import CharField
from psycopg2.extensions import adapt


def quotes(wordlist):
    return ["%s" % adapt(x.replace("\\", "").encode('utf-8')) for x in wordlist]


def startswith(wordlist):
    return [x + ":*" for x in quotes(wordlist)]


def negative(wordlist):
    return ['!' + x for x in startswith(wordlist)]


class VectorField(models.Field):
    """
        Stores Postgres ts_vector content, which we use to do blazing-fast searches on text-based
        content. See: http://www.postgresql.org/docs/9.1/static/functions-textsearch.html
    """

    def __init__(self, *args, **kwargs):
        kwargs['null'] = True
        kwargs['default'] = ''
        kwargs['editable'] = False
        kwargs['serialize'] = False
        kwargs['db_index'] = True

        super(VectorField, self).__init__(*args, **kwargs)

    def db_type(self, *args, **kwargs):
        """
            Returns the Postgres field type that this Django field type uses. This info is used by the
            Django ORM when creating tables that use this field type.
        """
        return 'tsvector'

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        return self.get_prep_lookup(lookup_type, value)

    def get_prep_value(self, value):
        return value


class TSConfig(object):

    def __init__(self, name):
        self.name = name


class TSBase(Lookup):

    def as_sql(self, qn, connection):

        lhs, lhs_params = qn.compile(self.lhs)
        rhs, rhs_params = self.process_rhs(qn, connection)

        if type(rhs_params) in [str, unicode]:
            rhs_params = [rhs_params]

        if type(rhs_params[0]) == TSConfig:

            ts = rhs_params.pop(0)
            ts_name = ts.name
            cmd = '%s @@ to_tsquery(%%s::regconfig, %%s)' % lhs

            rest = (ts_name, " & ".join(self.transform.__call__(rhs_params)))

        else:
            cmd = '%s @@ to_tsquery(%%s)' % lhs
            rest = (" & ".join(self.transform.__call__(rhs_params)),)

        return cmd, rest


class TSExact(TSBase):
    """
        Finds rows that EXACTLY MATCH all of the supplied tokens

        CASE 1: SINGLE TOKEN
        -----------------------------------------------------------
        Input: Model.objects.filter(search_field__ft='Foobar')
        Output: ts_query('foobar')

        CASE 2: MULTIPLE TOKENS
        -----------------------------------------------------------
        Input: Model.objects.filter(search_field__ft=['Foobar', 'Baz', 'Quux'])
        Output: ts_query('foobar & baz & quux')

        CASE 3: MULTIPLE TOKENS WITH LANGUAGE
        -----------------------------------------------------------
        Input: Model.objects.filter(search_field__ft=[TextSearchDictionary('french'),'Le Foobar', 'Le Baz'])
        Output: ts_query('french', '''le foobar'' & ''le baz''')
    """

    lookup_name = 'ft_exact'

    def transform(self, *args):
        # Django now passes-in multiple keys as a LIST instead of as positional args
        return quotes(args[0][0])


class TSStartsWith(TSBase):
    """
        Finds rows that BEGIN with all of the supplied token fragments

        Input: Model.objects.filter(search_field__ft_startswith=['Foobar', 'Baz', 'Quux'])
        Output: ts_query('foobar:* & baz:* & quux:*')
    """
    lookup_name = 'ft_startswith'

    def transform(self, *args):
        # Django now passes-in multiple keys as a LIST instead of as positional args
        return startswith(args[0][0])


class TSPhraseStartsWith(TSBase):
    """
        Finds rows that EXACTLY MATCH with all but the last token in the string, and which
        contain a token which BEGINS with the final token in the string

        Input: Model.objects.filter(search_field__ft_phrase_startswith=['foo Bar ba'])
        Output: ts_query('foo & bar & ba:*')
    """

    lookup_name = 'ft_phrase_startswith'

    def transform(self, *args):

        # Django now passes-in multiple keys as a LIST instead of as positional args
        quoted = quotes(args[0][0])

        items_left = len(quoted)

        result = []

        for token in quoted:

            items_left -= 1

            if items_left > 0:
                result.append(token)
            else:
                result.append(token + ":*")

        return result


class TSNotStartsWith(TSBase):
    """
        Finds rows that DO NOT BEGIN with all of the supplied token fragments

        Input: Model.objects.filter(search_field__ft=['Foobar', 'Baz', 'Quux'])
        Output: ts_query('!foobar:* & !baz:* & !quux:*')
    """

    lookup_name = 'ft_not_startswith'

    def transform(self, *args):
        # Django now passes-in multiple keys as a LIST instead of as positional args
        return negative(args[0][0])


class TSExpression(TSBase):
    """
        Finds rows that match a search string following basic "Google Syntax"

        Input: '"fat cats" -rats "kittens-" -"small-cats"'
        Output: ts_query('''fat cats''' & '''kittens-''' & !('''rats''' | '''small-cats'''))
    """

    lookup_name = 'ft_expression'

    def transform(self, *args):
        # 1) Its normal for the query going to postgres to have six ' characters. The postgres spec is to
        #    escape the ' character by doubling it. Psycopg2 follows this spec. We HAVE to wrap tsvector
        #    query strings in triple quotes per the postgres tsvector syntax.
        #
        #    Eg: to_tsquery('''''''fat cats'''''' & ...
        #
        # 2) Its normal for all of the ' characters to be preceded by a \ character when printing to
        #    console. Python prints the SQL as strings in quotes ('text'), and when a string contains
        #    a quote character, it has to be escaped with a \ when pretty-printed. The string doesn't
        #    actually contain the \ character.
        #
        #    Eg: to_tsquery(\'\'\'\'\'\'\'fat cats\'\'\'\'\'\' & ...
        #

        # Since this operator is intended to parse a STRING, we only use the first parameter passed in
        return [parse_fts_query(args[0][0])]


VectorField.register_lookup(TSExact)
VectorField.register_lookup(TSStartsWith)
VectorField.register_lookup(TSPhraseStartsWith)
VectorField.register_lookup(TSNotStartsWith)
VectorField.register_lookup(TSExpression)


class TSRank(Aggregate):
    function = 'ts_rank'
    name = 'TSRank'
    template = '%(function)s(%(expressions)s, to_tsquery(\'english\', %(ts_query_str)s))'

    def __init__(self, expression, **extra):
        if 'ft_expression' in extra:
            tsv = parse_fts_query(extra['ft_expression'], raw_sql=True)

        super(TSRank, self).__init__(expression, ts_query_str=tsv, output_field=CharField())

    def __repr__(self):
        return "{}({})".format(

            self.__class__.__name__,
            self.arg_joiner.join(str(arg) for arg in self.source_expressions)
        )
