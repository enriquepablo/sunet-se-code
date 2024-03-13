#!/bin/bash

DIRECTORY=$1

find "$DIRECTORY" -type f -name "*.md" | while IFS= read -r file; do
    awk '
    BEGIN {print "---"; inParagraph=1}
    /^$/ && inParagraph {print "---\n"; inParagraph=0; next}
    {print}
    ' "$file" > tmpfile && mv tmpfile "$file"
done
