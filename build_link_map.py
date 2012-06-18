#!/usr/bin/env python

#   Copyright (C) 2012  p12 <tir5c3@yahoo.co.uk>
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

# This file examines all html files in the output directory and writes
# filename -> title mapping to a xml file.

import fnmatch
import re
import os

# find all html files
html_files = []
for root, dirnames, filenames in os.walk('output'):
    for filename in fnmatch.filter(filenames, '*.html'):
        html_files.append(os.path.join(root, filename))

# create an xml file containing mapping between page title and actual location
out = open('link-map.xml', 'w')
out.write('<?xml version="1.0" encoding="UTF-8"?><files>\n')

for fn in html_files:
    f = open(fn, "r")
    text = f.read()
    f.close()

    m = re.search('<script>[^<]*mw\.config\.set([^<]*wgPageName[^<]*)</script>', text)
    if not m:
        continue
    text = m.group(1)
    text = re.sub('\s*', '', text)
    m = re.search('"wgPageName":"([^"]*)"', text)
    if not m:
        continue

    title = m.group(1)

    target = os.path.relpath(os.path.abspath(fn), os.path.abspath('output'))
    out.write('  <file from="' + title + '" to="' + target + '" />\n')

out.write('</files>')
out.close()
