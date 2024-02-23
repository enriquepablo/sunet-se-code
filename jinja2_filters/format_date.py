from babel.dates import format_date as fd


def format_date(value, format='long', lang='sv'):
    return fd(value, format=format, locale=lang)
