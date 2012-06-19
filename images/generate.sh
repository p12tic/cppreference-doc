#!/bin/bash
#   Copyright (C) 2011, 2012  p12 <tir5c3@yahoo.co.uk>
#
#   This file is part of cppreference-doc
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see http://www.gnu.org/licenses/.

mkdir -p "output"

for i in $(find -iname "*.dot")
do
    infile="$i"
    outfile="output/$i.svg"
    mapfile="output/$i.map"
    tmpfile="output/$i.tmp"
    dot -Tsvg -o$tmpfile $infile
    dot -Timap $infile | sed 1d | awk '{sub(/,/, " ", $3); sub(/,/, " ", $4); print $1" "$3" "$4" [["$2"]]"; };' > $mapfile
    xsltproc --novalid fix_svg-dot.xsl $tmpfile > $outfile
    rm $tmpfile
done

python math.py
