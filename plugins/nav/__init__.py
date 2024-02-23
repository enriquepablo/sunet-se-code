from collections import defaultdict
from urllib.parse import urljoin
import logging
import os

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from pelican import signals
from pelican.contents import Content


log = logging.getLogger(__name__)


def build_people(pelican):

    if 'ES_PEOPLE' in pelican.settings:
        del pelican.settings['ES_PEOPLE']

    base_path = pelican.settings['INSTALL_DIR']
    people_path = os.path.join(base_path, 'content', 'people')
    people_filenames = os.listdir(people_path)

    people = {}

    for filename in people_filenames:

        person_path = os.path.join(people_path, filename)
        with open(person_path, 'r') as f:
            preperson = yaml.load(f, Loader=Loader)
            person = {'role': {}}
            for key in preperson:
                if key.startswith('Role'):
                    lang = key.split('_')[1]
                    person['role'][lang] = preperson[key]
                elif preperson[key] is not None:
                    person[key.lower()] = preperson[key]
                else:
                    person[key.lower()] = ''

        people[person['slug']] = person

    pelican.settings['ES_PEOPLE'] = people


def build_categories(pelican):

    if 'ES_SCATS' in pelican.settings:
        del pelican.settings['ES_SCATS']

    base_path = pelican.settings['INSTALL_DIR']
    cats_path = os.path.join(base_path, 'content', 'navigation', 'service-categories')
    cats_filenames = os.listdir(cats_path)

    cats = []

    for filename in cats_filenames:

        cat_path = os.path.join(cats_path, filename)
        with open(cat_path, 'r') as f:
            precat = yaml.load(f, Loader=Loader)
            cat = {'title': {}}
            for key in precat:
                if key.startswith('Title'):
                    lang = key.split('_')[1]
                    cat['title'][lang] = precat[key]
                elif precat[key] is not None:
                    cat[key.lower()] = precat[key]
                else:
                    cat[key.lower()] = ''

        cats.append(cat)

    cats.sort(key=lambda c: c['order'])
    pelican.settings['ES_SCATS'] = cats


def build_menus(pelican):

    if 'ES_MENUS' in pelican.settings:
        del pelican.settings['ES_MENUS']

    base_path = pelican.settings['INSTALL_DIR']
    menus_path = os.path.join(base_path, 'content', 'navigation', 'menus')
    menu_filenames = os.listdir(menus_path)

    menus = defaultdict(dict)

    for filename in menu_filenames:
        menu_bits = filename.split('.')[0].split('-')
        menu_name = '-'.join(menu_bits[:-1])
        lang = menu_bits[-1]
        menus[menu_name][lang] = []

        menu_path = os.path.join(menus_path, filename)
        with open(menu_path, 'r') as f:
            menu = yaml.load(f, Loader=Loader)

        for key, value in menu.items():
            external = False
            if '://' in value and pelican.settings['ES_SITEURL'] not in value:
                external = True

            menus[menu_name][lang].append({'title': key, 'url': value, 'external': external})

    pelican.settings['ES_MENUS'] = menus


def build_footer(pelican):

    if 'ES_FOOTER' in pelican.settings:
        del pelican.settings['ES_FOOTER']

    base_path = pelican.settings['INSTALL_DIR']
    footer_path = os.path.join(base_path, 'content', 'navigation', 'footer')
    footer_filenames = os.listdir(footer_path)

    footer = {
        'entries': defaultdict(list),
        'address': {},
        'address-meta': {}
    }

    for filename in footer_filenames:
        entry_bits = filename.split('.')[0].split('-')
        entry_name = '-'.join(entry_bits[:-1])
        lang = entry_bits[-1]

        entry_path = os.path.join(footer_path, filename)
        with open(entry_path, 'r') as f:

            if entry_name in ('address', 'address-meta'):
                footer[entry_name][lang] = f.read()
            else:
                data = yaml.load(f, Loader=Loader)
                footer['entries'][lang].append(data)

    for lang in pelican.settings['LANGS']:
        if lang in footer['entries']:
            footer['entries'][lang].sort(key=lambda entry: entry['Order'])

    pelican.settings['ES_FOOTER'] = footer


def build_navigation(pelican):
    build_people(pelican)
    build_categories(pelican)
    build_menus(pelican)
    build_footer(pelican)


def add_url(content):
    content.abs_url = urljoin('/', content.url)


def register():
    signals.initialized.connect(build_navigation)
    signals.content_object_init.connect(add_url)
