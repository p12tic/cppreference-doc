#!/bin/bash

#   Copyright (C) 2011  p12 <tir5c3@yahoo.co.uk>
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

page="$1"
# remove an invalid tag added by httrack
sed -f "fix_html-httrack_meta.sed" -i "$page"

# remove sidebar, header and footer
xsltproc --novalid --html -o "tmpfile" "fix_html-cleanup.xsl" $1 
mv "tmpfile" "$page"


