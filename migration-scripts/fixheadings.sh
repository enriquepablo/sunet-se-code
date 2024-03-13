#!/bin/bash

# Directory to start searching from
DIRECTORY=$1

# Find all markdown files and process them
find "$DIRECTORY" -type f -name "*.md" | while IFS= read -r file; do
    awk '
    {
        if (length(prevLine) > 0 && /^-{7,}$/) {
            print "## " prevLine
            getline
        } else {
            if (NR > 1) print prevLine
        }
        prevLine = $0
    }
    END {
        print prevLine
    }
    ' "$file" > tmpfile && mv tmpfile "$file"
done
