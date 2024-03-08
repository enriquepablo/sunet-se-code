#!/bin/bash

# Loop through each file passed as a parameter
for file in "$@"; do
    # Read the first line of the file
    first_line=$(head -n 1 "$file")

    # Extract the title from the first line
    title=$(echo "$first_line" | sed 's/^Title: //')

    # Rename the file to the title with .md extension
    new_filename="$title.md"
    git mv "$file" "$new_filename"

    echo "Renamed $file to $new_filename"
done
