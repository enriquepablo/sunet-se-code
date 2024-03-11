from collections import defaultdict
from urllib.parse import urljoin
import json
import logging
import os
import shutil

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from pelican import signals
from pelican.contents import Content


CONTENT_DIR = 'sunet-se-content'


log = logging.getLogger(__name__)


def build_people(pelican):

    if 'ES_PEOPLE' in pelican.settings:
        del pelican.settings['ES_PEOPLE']

    base_path = pelican.settings['INSTALL_DIR']
    people_path = os.path.join(base_path, CONTENT_DIR, 'people')
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
    service_path = os.path.join(base_path, CONTENT_DIR, 'navigation', 'service-categories')
    service_filenames = os.listdir(service_path)
    projekt_path = os.path.join(base_path, CONTENT_DIR, 'navigation', 'projekt-categories')
    projekt_filenames = os.listdir(projekt_path)

    service_cats = []
    projekt_cats = []

    for path, filenames, cats in (service_path, service_filenames, service_cats), (projekt_path, projekt_filenames, projekt_cats):

        for filename in filenames:
            cat_path = os.path.join(path, filename)
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

    pelican.settings['ES_SCATS'] = {
        'services': service_cats,
        'projekt': projekt_cats,
    }


def build_menus(pelican):

    if 'ES_MENUS' in pelican.settings:
        del pelican.settings['ES_MENUS']

    base_path = pelican.settings['INSTALL_DIR']
    menus_path = os.path.join(base_path, CONTENT_DIR, 'navigation', 'menus')
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
    footer_path = os.path.join(base_path, CONTENT_DIR, 'navigation', 'footer')
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


def build_tickets(pelican):

    if 'ES_TICKETS' in pelican.settings:
        del pelican.settings['ES_TICKETS']

    pelican.settings['ES_TICKETS'] = {}

    base_path = os.environ.get('JIRA_TICKETS_OUTPUT', '')
    json_path = os.path.join(base_path, 'tickets.json')

    if base_path == '' or not os.path.exists(json_path):
        return

    json_path = os.path.join(base_path, 'tickets.json')
    with open(json_path) as f:
        tickets = json.loads(f.read())

    open_tickets = list(filter(lambda ticket: ticket['fields']['status']['name'] == 'Open' or ticket['fields']['status']['name'] == 'Resolved', tickets))
    sched_tickets = list(filter(lambda ticket: ticket['fields']['issuetype']['name'].strip() == "Scheduled" and 'customfield_11603' in ticket['fields'] and ticket['fields']['customfield_11603'] is not None, open_tickets))
    unsched_tickets = list(filter(lambda ticket: ticket['fields']['issuetype']['name'].strip() == "Unscheduled", open_tickets))

    pelican.settings['ES_TICKETS']['open_tickets'] = {}
    for ticket in open_tickets:
        pelican.settings['ES_TICKETS']['open_tickets'][ticket['key']] = ticket

    for item in sched_tickets:
        if item['fields'].get('customfield_11603', None) is not None:
            startend = item['fields']['customfield_11603'].split('/')
            item['start'] = startend[0]

    for item in unsched_tickets:
        item['start'] = item['fields']['created']

    sched_tickets.sort(key=lambda t: t['start'])
    unsched_tickets.sort(key=lambda t: t['start'])

    for tickets in sched_tickets, unsched_tickets:
        for ticket in tickets:
            ticket['affected_customers'] = []
            ticket['affected_services'] = []
            if 'customfield_11600' in ticket['fields'] and ticket['fields']['customfield_11600']:
                for item in ticket['fields']['customfield_11600']:
                    affected = item.split(':')[-1]
                    if item.startswith('affected_customer'):
                        ticket['affected_customers'].append(affected)
                    elif item.startswith('service'):
                        ticket['affected_services'].append(affected)

    tickets_path = os.path.join(pelican.settings['INSTALL_DIR'], CONTENT_DIR, 'pages', 'arenden')
    if os.path.exists(tickets_path):
        shutil.rmtree(tickets_path)

    os.makedirs(tickets_path)

    for tickets in sched_tickets, unsched_tickets:
        for ticket in tickets:
            print(f"ticket {ticket['key']}")
            filename = f"{ticket['key']}.md"
            path = os.path.join(tickets_path, filename)
            print(f"path {path}")
            with open(path, 'w') as f:
                f.write(f"Title: {ticket['key']}\n")
                f.write(f"Slug: arenden/{ticket['key']}\n")
                f.write(f"Summary: {ticket['fields']['summary']}\n")

    pelican.settings['ES_TICKETS']['scheduled'] = sched_tickets
    pelican.settings['ES_TICKETS']['unscheduled'] = unsched_tickets


def build_navigation(pelican):
    build_people(pelican)
    build_categories(pelican)
    build_menus(pelican)
    build_footer(pelican)
    build_tickets(pelican)


def add_url(content):
    content.abs_url = urljoin('/', content.url)


def register():
    signals.initialized.connect(build_navigation)
    signals.content_object_init.connect(add_url)
