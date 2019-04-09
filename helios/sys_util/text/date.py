#  -*- coding: UTF8 -*-

from datetime import datetime, date

from dateutil.relativedelta import relativedelta


def render_interval(start, end):
    """
        Renders a date object for the front-end

        :param start: start date
        :param end: end date
        :return: rendered interval string
    """

    if end:
        end_str = end.strftime('%B %Y')

    else:
        end = datetime.now()
        end_str = 'Present'

    # Advance the end date by 1 month so that the current month is counted towards the interval
    diff = relativedelta((end + relativedelta(months=1)), start)

    years = diff.years
    months = diff.months

    base = ' ('

    if years:
        base += str(years) + ' year' + ('s' if years > 1 else '')

    if years and months:
        base += ' '

    if months:
        base += str(months) + ' month' + ('s' if months > 1 else '')

    base += ')'

    return start.strftime('%B %Y') + ' - ' + end_str + base


def render_year_interval(start, end):
    """
        Renders a date object for the front-end

        :param start: start date
        :param end: end date
        :return: rendered interval string
    """

    if end:
        end_str = end.strftime('%Y')

    else:
        end_str = 'Present'

    return start.strftime('%Y') + ' - ' + end_str


def render_year_list(val=None, date=None):
    """
        Renders a list of items for a year dropdown

        :param val: If passed, the year in the list that matches val will be selected
        :param date: Date object. If passed, the year in the list that matches the date object will be selected
        :return: list of rendered option strings
    """

    match_year = date.strftime('%Y') if date else None

    result = []

    for year in range(2016, 1980, -1):
        selected = ' selected="selected"' if ((str(year) == match_year) or (str(year) == val)) else ''

        result.append('<option value="{}"{}>{}</option>'.format(str(year), selected, str(year)))

    return result


def render_month_list(val=None, date=None):
    """
        Renders a list of items for a month dropdown

        :param val: If passed, the month in the list that matches val will be selected
        :param date: Date object. If passed, the month in the list that matches the date object will be selected
        :return: list of rendered option strings
    """

    months = [

        ('01', 'Jan'),
        ('02', 'Feb'),
        ('03', 'Mar'),
        ('04', 'Apr'),
        ('05', 'May'),
        ('06', 'Jun'),
        ('07', 'Jul'),
        ('08', 'Aug'),
        ('09', 'Sep'),
        ('10', 'Oct'),
        ('11', 'Nov'),
        ('12', 'Dec')
    ]

    match_month = date.strftime('%m') if date else None

    result = []

    for num, txt in months:
        selected = ' selected="selected"' if ((num == match_month) or (num == val)) else ''

        result.append('<option value="{}"{}>{}</option>'.format(num, selected, txt))

    return result


def render_day_list(val=None, date=None):
    """
        Renders a list of items for a date dropdown

        :param val: If passed, the day in the list that matches val will be selected
        :param date: Date object. If passed, the day in the list that matches the date object will be selected
        :return: list of rendered option strings
    """

    match_day = date.strftime('%d') if date else None

    result = []

    for day in [str(d) if d > 9 else '0' + str(d) for d in range(1, 32)]:
        selected = ' selected="selected"' if ((day == match_day) or (day == val)) else ''

        result.append('<option value="{}"{}>{}</option>'.format(day, selected, day))

    return result


def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))
