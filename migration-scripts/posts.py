#!/bin/env python

import json
import os
import sys

from markdownify import markdownify

output_filename_news = 'output-news'
output_filename_blog = 'output-blog'

if not os.path.exists(output_filename_news):
    os.makedirs(output_filename_news)

if not os.path.exists(output_filename_blog):
    os.makedirs(output_filename_blog)

# read file, json
json_filename = sys.argv[1]

with open(json_filename, 'r') as json_file:
    data = json.loads(json_file.read())

    # loop over files
    for post in data:
        # get slug, open file
        slug = post['slug']
        lang = post['lang']
        if lang != 'sv':
            continue

        is_news = post['acf']['is_news_item']

        status = post['status']
        if status == 'publish':
            status = 'published'

        cat = 'blogg'
        fname = os.path.join(output_filename_blog, f"{slug}.md")
        slug_long = f"om-sunet/aktuellt/blogg/{slug}"
        if is_news:
            cat = 'nyheter'
            fname = os.path.join(output_filename_news, f"{slug}.md")
            slug_long = f"om-sunet/aktuellt/nyheter/{slug}"

        translation = "false" if lang == "sv" else "true"

        with open(fname, "w") as file:
            md = markdownify(post['content']['rendered'])
            if "<img" in md:
                print(slug)
                continue
            # get md, put in file
            file.write(f"Title: {post['title']['rendered']}\n")
            file.write(f"Date: {post['date']}\n")
            file.write(f"Modified: {post['modified']}\n")
            file.write(f"Slug: {slug_long}\n")
            file.write(f"Status: {status}\n")
            file.write(f"Category: {cat}\n")
            file.write("Authors: \n")
            file.write(f"Lang: {lang}\n")
            file.write(f"Translation: {translation}\n\n")

            # get text, convert to markdown, write
            file.write(md)

