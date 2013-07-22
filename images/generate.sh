#!/bin/bash
#   Copyright (C) 2011, 2012  Povilas Kanapickas <tir5c3@yahoo.co.uk>
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
mkdir -p "output/inheritance"

for i in $(find inheritance -iname "*.dot")
do

    o=${i#*/}

    outdir="output/inheritance/"
    infile="$i"
    setfile="inheritance/settings-dot"
    outfile="$outdir/$o.svg"
    mapfile="$outdir/$o.map"
    wikimapfile="$outdir/$o.wikimap"
    tmpsvgfile="$outdir/$o.tmpsvg"
    tmpdotfile="$outdir/$o.tmpdot"

    python preprocess.py $infile $setfile $tmpdotfile
    dot -Tsvg -o$tmpsvgfile $tmpdotfile
    xsltproc --novalid fix_svg-dot.xsl $tmpsvgfile > $outfile
    dot -Timap $tmpdotfile | sed 1d | awk '{sub(/,/, " ", $3); sub(/,/, " ", $4); print $1" "$3" "$4" [["$2"]]"; };' > $mapfile

    wikiimage=$(echo $o | sed 's/\.\///' | sed 's/\.dot//')
    echo "{{inheritance diagram|image=$wikiimage.svg|notes={{{notes|}}}|map=" > $wikimapfile
    cat $mapfile >> $wikimapfile
    echo "}}" >> $wikimapfile

    rm $tmpsvgfile
    rm $tmpdotfile
done

python math.py
