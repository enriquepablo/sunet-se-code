#!/bin/env python

import json
import os
import sys

from markdownify import markdownify

output_filename = 'output-events'

if not os.path.exists(output_filename):
    os.makedirs(output_filename)

# read file, json
json_filename = sys.argv[1]

with open(json_filename, 'r') as json_file:
    data = json.loads(json_file.read())

    # loop over files
    for event in data:
        # get slug, open file
        slug = event['slug']
        lang = event['lang']
        if lang != 'sv':
            continue

        status = event['status']
        if status == 'publish':
            status = 'published'

        cat = 'evenemang'
        fname = os.path.join(output_filename, f"{slug}.md")
        slug_long = f"om-sunet/aktuellt/evenemang/{slug}"

        translation = "false" if lang == "sv" else "true"

        with open(fname, "w") as file:
            md = markdownify(event['content']['rendered'])
            if "<img" in md:
                print(slug)
                continue
            # get md, put in file
            file.write(f"Title: {event['title']['rendered']}\n")
            file.write(f"Date: {event['date']}\n")
            file.write(f"Modified: {event['modified']}\n")
            file.write(f"EventDate: {event['acf']['text_date']}\n")
            file.write(f"Slug: {slug_long}\n")
            file.write(f"Status: {status}\n")
            file.write("Category: evenemang\n")
            file.write("Authors: \n")
            file.write(f"Lang: {lang}\n")
            file.write(f"Translation: {translation}\n\n")

            # get text, convert to markdown, write
            file.write(md)


