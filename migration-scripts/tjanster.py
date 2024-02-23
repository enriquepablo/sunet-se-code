#!/bin/env python

import json
import os
import sys

from markdownify import markdownify

# read file, json
json_filename = sys.argv[1]
json_cats_filename = sys.argv[2]

output_filename = 'output-services'

if not os.path.exists(output_filename):
    os.makedirs(output_filename)

with open(json_filename, 'r') as json_file:
    data = json.loads(json_file.read())

    with open(json_cats_filename, 'r') as json_cats_file:
        cats = json.loads(json_cats_file.read())

        # loop over files
        for service in data:
            # get slug, open file
            slug = service['slug']
            lang = service['lang']
            if lang != 'sv':
                continue

            status = service['status']
            if status == 'publish':
                status = 'published'

            person_slug = ''
            person = service['acf']['person']
            if person:
                person_slug = person[0]['post_name']

            category = ''
            for cat in cats:
                if service['categories'][0] == cat['id']:
                    category = cat['name']
                    break

            fname = ''
            if category:
                category_path = os.path.join(output_filename, category.lower())
                if not os.path.exists(category_path):
                    os.makedirs(category_path)
                fname = os.path.join(category_path, f"{slug}.md")
                slug_long = f"services/{category.lower()}/{slug}"
            else:
                continue

            translation = "false" if lang == "sv" else "true"

            with open(fname, "w") as file:
                md = markdownify(service['acf']['content'])
                if "<img" in md:
                    print(slug)
                    continue
                # get md, put in file
                file.write(f"Title: {service['title']['rendered']}\n")
                file.write(f"Subtitle: {service['acf']['intro']}\n")
                file.write(f"Date: {service['date']}\n")
                file.write(f"Modified: {service['modified']}\n")
                file.write(f"Slug: {slug_long}\n")
                file.write(f"Status: {status}\n")
                file.write(f"Contact: {person_slug}\n")
                file.write(f"Category: {category}\n")
                file.write("Authors: \n")
                file.write(f"Lang: {lang}\n")
                file.write(f"Translation: {translation}\n\n")

                # get text, convert to markdown, write
                file.write(md)

