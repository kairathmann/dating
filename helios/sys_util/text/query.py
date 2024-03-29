#  -*- coding: UTF8 -*-

import re, unicodedata


def parse_fts_query(query, raw_sql=False):
    """
        Converts an unsanitized query string into a sanitized expression that can be passed to Postgres
        to_tsvector(). Syntax supports quoted phrase matching and exclusion. Automatically fixes unbalanced
        quoted phrases ("fat cats" rats"), multiple dashes, etc.

        Example query string: '"fat cats" -rats "kittens-" -"small-cats"'

        :param query: (almost) any possible string
        :param raw_sql: return an escaped string suitable for injection directly into a query

        :return: to_tsvector() expression
    """

    # ABOUT the 'raw_sql' flag
    # ============================================================================================
    # In most cases, the expression generated by this function will be passed in to psycopg2 as a PARAMETER,
    # in which case psycopg2 will "wrap" it in an additional pair of quotes, and replace every block of
    # triple-quotes with a block of 6 quotes:
    #
    # BEFORE: '''fat cats''' & '''kittens-''' & !('''rats''' | '''small-cats''')
    # AFTER: '''''''fat cats'''''' & ''''''kittens-'''''' & !(''''''rats'''''' | ''''''small-cats'''''')'
    #
    # However, when Django is passed a named parameter via a custom aggregation function, for some
    # reason it injects it as a raw string instead of escaping it. Since Django's ORM has ZERO developer
    # documentation, determining the cause of this could easily take a week of reverse-engineering
    # their code. So instead, we'll just escape the string ourselves for now.

    # Balance quotes
    # =============================================================================

    if (query.count('"') % 2) != 0:
        offset = query.rfind('"', 0)
        query = query[:offset] + query[offset + 1:]

    # Remove repeated spaces, repeated dashes, and unattached negation dashes
    # =============================================================================

    previous = None

    while previous != query:
        previous = query
        query = re.sub(r'([-])\1', '', query)
        query = re.sub(r' - ', ' ', query)
        query = re.sub(r'([ ])\1', '', query)

    # Convert the inbound string to UTF-8, if necessary, to avoid common errors
    if isinstance(query, str):
        query = unicode(query, "utf-8")

    # Break query into tokens
    # =============================================================================

    include_tokens = []
    exclude_tokens = []

    chars_remaining = len(query)
    is_neg = False
    in_token = False
    stack = ''

    for char in query:

        chars_remaining -= 1

        # CASE 1: Starting or ending a quoted token
        # --------------------------------------------------------

        if char == '"':

            if not in_token:

                in_token = True

            else:

                if stack:

                    if is_neg:
                        exclude_tokens.append(stack)
                    else:
                        include_tokens.append(stack)

                in_token = False
                is_neg = False
                stack = ''

        # CASE 2: Space character
        # --------------------------------------------------------

        elif char == ' ':

            # Inside quoted token
            if in_token:

                stack += char

            # Terminating an unquoted token
            elif stack:

                if is_neg:
                    exclude_tokens.append(stack)
                else:
                    include_tokens.append(stack)

                is_neg = False
                stack = ''

        # CASE 3: Starting a negated block or transcribing a "-"
        # --------------------------------------------------------

        elif char == '-':

            if not stack:
                is_neg = True

            else:
                stack += char

        # CASE 4: Any other character
        # --------------------------------------------------------
        elif char != ' ':

            stack += char

            if not chars_remaining:

                if is_neg:
                    exclude_tokens.append(stack)
                else:
                    include_tokens.append(stack)

    # Sanitize Tokens
    # =============================================================================

    include_tokens_clean = [clean_token(token) for token in include_tokens if clean_token(token)]
    exclude_tokens_clean = [clean_token(token) for token in exclude_tokens if clean_token(token)]

    # Assemble into to_tsvector() expression
    # =============================================================================

    fts_expression = ''

    tokens_remaining = len(include_tokens_clean)

    for token in include_tokens_clean:

        tokens_remaining -= 1

        # SECURITY CRITICAL:
        # ########################################
        # Do not remove the triple quotes ('''')

        if raw_sql:
            fts_expression += "''''''" + token + "''''''"
        else:
            fts_expression += "'''" + token + "'''"

        if tokens_remaining:
            fts_expression += ' & '

    if include_tokens_clean and exclude_tokens_clean:
        fts_expression += " & "

    if exclude_tokens_clean:

        fts_expression += "!("

        tokens_remaining = len(exclude_tokens_clean)

        for token in exclude_tokens_clean:

            tokens_remaining -= 1

            # SECURITY CRITICAL:
            # ########################################
            # Do not remove the triple quotes ('''')

            if raw_sql:
                fts_expression += "''''''" + token + "''''''"
            else:
                fts_expression += "'''" + token + "'''"

            if tokens_remaining:
                fts_expression += ' | '

        fts_expression += ")"

    if raw_sql:
        return "'" + fts_expression + "'"
    else:
        return fts_expression


def clean_token(token):
    """
        Strips unsafe punctuation out of a UTF-8 token string

        :param token: token to sanitize
        :return:sanitized token
    """

    # SECURITY CRITICAL:
    # ##########################################################################################################
    # Do not add any other characters, including but not limited to [' * & ! @ ( ) /\ | + ;] to the whitelist. All
    # of these characters have significance in a tsvector query, and there's no guarantee that psycopg2 will
    # properly escape them

    whitelist = '-_.$#%'

    result = ''

    for char in token:

        if (unicodedata.category(char) != 'Po') or (char in whitelist):
            result += char

    return result
