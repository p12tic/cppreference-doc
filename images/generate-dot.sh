#!/bin/bash

for i in $(find -iname "*.dot")
do
    infile="$i"
    outfile="$i".svg
    mapfile="$i".map
    tmpfile="$i".tmp
    dot -Tsvg -o$tmpfile $infile
    dot -Timap $infile | sed 1d | awk '{sub(/,/, " ", $3); sub(/,/, " ", $4); print $1" "$3" "$4" [["$2"]]"; };' > $mapfile
    xsltproc --novalid fix_svg.xsl $tmpfile > $outfile
    rm $tmpfile
done
