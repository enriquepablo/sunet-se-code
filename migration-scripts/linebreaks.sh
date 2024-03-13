#!/bin/bash

# Directory to start searching from, provided as the first command line argument
DIRECTORY=$1

# Find all markdown files and process them
find "$DIRECTORY" -type f -name "*.md" | while IFS= read -r file; do
    # Use perl to replace sequences of more than two line breaks with exactly two line breaks
    perl -0777 -i -pe 's/\n{3,}/\n\n/g' "$file"
done
