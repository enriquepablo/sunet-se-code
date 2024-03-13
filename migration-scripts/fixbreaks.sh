#!/bin/bash

# Directory to start searching from
DIRECTORY=$1

# Find all markdown files and process them
find "$DIRECTORY" -type f -name "*.md" | while IFS= read -r file; do
    # Use sed to replace the patterns in-place
    sed -i -z 's/  \n[ >]*\n/  \n/g' "$file"
done
