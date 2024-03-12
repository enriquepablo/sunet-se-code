import os
import sys


AUTHOR = 'Sunet'
SITENAME = 'Sunet'
SITEURL = ""

THEME = 'theme'

PATH = "sunet-se-content"

DIRECT_TEMPLATES = ['index', 'archives']

INSTALL_DIR = os.path.split(os.path.abspath(__name__))[0]

PAGE_PATHS = ['pages']

ARTICLE_PATHS = ['articles']

PAGE_EXCLUDES = ['templates', 'navigation', 'wp-content', 'people', '_Documentation']

ARTICLE_EXCLUDES = ['templates', 'navigation', 'wp-content', 'people', '_Documentation']

STATIC_PATHS = ['wp-content']

JINJA_ENVIRONMENT = {
    'extensions': ['jinja2.ext.i18n'],
}
sys.path.append('jinja2_filters')

from format_date import format_date
JINJA_FILTERS = {'format_date': format_date}

THEME_STATIC_PATHS = ['static', 'assets']
THEME_STATIC_DIR = 'static'

# OUTPUT_RETENTION = ['static']

PLUGIN_PATHS = ["plugins"]
PLUGINS = ["i18n_subsites", "webassets", "nav"]

TIMEZONE = 'Europe/Stockholm'

DEFAULT_LANG = 'sv'
LANG = 'sv'

I18N_SUBSITES = {
    'en': {
        'SITENAME': 'Sunet',
        'LANG': 'en',
    }
}

LANGS = [LANG]
LANGS.extend(I18N_SUBSITES.keys())

PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

WEBASSETS_CONFIG = [
    ('POSTCSS_BIN', f'{INSTALL_DIR}/node_modules/postcss-cli/index.js'),
]

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ("Pelican", "https://getpelican.com/"),
    ("Python.org", "https://www.python.org/"),
    ("Jinja2", "https://palletsprojects.com/p/jinja/"),
    ("You can modify those links in your config file", "#"),
)

# Social widget
SOCIAL = (
    ("You can add links in your config file", "#"),
    ("Another social link", "#"),
)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

###################################################
# SUNET SPECIFIC SETTINGS
###################################################

ES_PAGINATION = 2

ES_SITEURL = "https://sunet.se"
