#!/bin/bash

page="$1"
# remove an invalid tag added by httrack
sed -f "fix_html-httrack_meta.sed" -i "$page"

# remove sidebar, header and footer
xsltproc --novalid --html -o "tmpfile" "fix_html-cleanup.xsl" $1 
mv "tmpfile" "$page"


