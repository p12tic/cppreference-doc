#!/usr/bin/env python

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

import fnmatch
import re
import os

# copy the source tree
os.system('rm -rf output')
os.system('mkdir output')
os.system('cp -rt output reference/*')

# find all html and css files
html_files = []
css_files = []
for root, dirnames, filenames in os.walk('output'):
    for filename in fnmatch.filter(filenames, '*.html'):
        html_files.append(os.path.join(root, filename))
    for filename in fnmatch.filter(filenames, '*.css'):
        css_files.append(os.path.join(root, filename))

#
r1 = re.compile('<!-- Added by HTTrack -->.*?<!-- \/Added by HTTrack -->')
r2 = re.compile('<!-- Mirrored from .*?-->')

# clean the html files
for fn in html_files:
    f = open(fn, "r")
    text = f.read()
    f.close()

    text = r1.sub('', text);
    text = r2.sub('', text);

    f = open(fn, "w")
    f.write(text)
    f.close()

    tmpfile = fn + '.tmp';
    os.system('xsltproc --novalid --html preprocess.xsl "' + fn + '" > "' + tmpfile + '"')
    os.system('mv "' + tmpfile + '" "' + fn + '"')


os.system('cat preprocess-css.css >> "output/en.cppreference.com/mwiki/load7fe1.css"')
