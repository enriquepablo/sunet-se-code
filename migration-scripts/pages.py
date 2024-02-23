#!/bin/env python

import json
import os
import sys

from markdownify import markdownify

# read file, json
json_filename = sys.argv[1]

output_filename = 'output-pages'

if not os.path.exists(output_filename):
    os.makedirs(output_filename)

with open(json_filename, 'r') as json_file:
    data = json.loads(json_file.read())

    # loop over files
    for page in data:
        # get slug, open file
        slug = page['slug']
        lang = page['lang']
        if lang != 'sv':
            continue

        status = page['status']
        if status == 'publish':
            status = 'published'

        fname = os.path.join(output_filename, f"{slug}.md")
        translation = "false" if lang == "sv" else "true"

        with open(fname, "w") as file:
            md = markdownify(page['content']['rendered'])
            if "<img" in md:
                print(slug)
                continue
            # get md, put in file
            file.write(f"Title: {page['title']['rendered']}\n")
            file.write(f"Date: {page['date']}\n")
            file.write(f"Modified: {page['modified']}\n")
            file.write(f"Slug: {page['slug']}\n")
            file.write(f"Status: {status}\n")
            file.write("Authors: \n")
            file.write(f"Lang: {lang}\n")
            file.write(f"Translation: {translation}\n\n")

            # get text, convert to markdown, write
            file.write(md)
