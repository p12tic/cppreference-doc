#!/bin/bash

for i in $(find -iname "*.dot")
do
    infile="$i"
    outfile="$i".svg
    tmpfile="$i".tmp
    dot -Tsvg -o$tmpfile $infile
    xsltproc --novalid fix_svg.xsl $tmpfile > $outfile
    rm $tmpfile
done
