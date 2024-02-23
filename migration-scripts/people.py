#!/bin/env python

import json
import os
import sys

from markdownify import markdownify

if not os.path.exists('output-people'):
    os.makedirs('output-people')

# read file, json
json_filename = sys.argv[1]

with open(json_filename, 'r') as json_file:
    data = json.loads(json_file.read())

    # loop over files
    for person in data:
        # get slug, open file
        slug = person['slug']
        lang = person['lang']
        if lang != 'sv':
            continue

        status = person['status']
        if status == 'publish':
            status = 'published'

        fname = os.path.join('output-people', f"{slug}.md")
        translation = "false" if lang == "sv" else "true"

        with open(fname, "w") as file:
            # get md, put in file
            file.write(f"Title: {person['title']['rendered']}\n")
            file.write(f"Date: {person['date']}\n")
            file.write(f"Modified: {person['modified']}\n")
            file.write(f"Slug: {person['slug']}\n")
            file.write(f"Status: {status}\n")
            file.write(f"Lang: {lang}\n")
            file.write(f"Visa: {person['acf'].get('visa', 'false')}\n")
            file.write(f"Email: {person['acf']['email']}\n")
            file.write(f"Phone: {person['acf']['phone']}\n")
            file.write(f"Role_sv: {person['acf']['title']}\n")
