#!/usr/bin/env python

#   Copyright (C) 2012  Povilas Kanapickas <tir5c3@yahoo.co.uk>
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

# This program downloads all files that have been forgotten by httrack
# Currently these files are images referred from the CSS files

import fnmatch
import re
import os

# find all css files
css_files = []
for root, dirnames, filenames in os.walk('reference'):
    for filename in fnmatch.filter(filenames, '*.css'):
        css_files.append(os.path.join(root, filename))

for fn in css_files:
    f = open(fn, "r")
    text = f.read()
    f.close()

    p_text = text

    # spaces within paths NOT supported
    # matches only those URLS starting with http://$(lang).cppreference.com
    text = re.sub('\s*', '', text)
    matches = re.findall(':url\(([^\'"][^\(]*[^\'"])\)', text)
    matches += re.findall(':url\(\'([^\']*)\'\)', text)
    matches += re.findall(':url\("([^\']*)"\)', text)

    for match in matches:
        p_match = match

        # strip query string
        match = re.sub('\?[^?]*$', '', match)

        if (not re.match('https?://', match)):
            continue
        match = re.sub('^https?://', '', match)
        if (not re.match('[^.]*\.cppreference\.com', match)):
            continue

        start = os.path.abspath(os.path.dirname(fn))
        dest = os.path.abspath('reference/' + match)

        os.system('rm -f "' + dest + '"')
        os.system('wget "' + p_match + '" -O "' + dest + '"')
        relpath = os.path.relpath(dest, start)

        p_text = p_text.replace(p_match, relpath)

    f = open(fn, "w")
    f.write(p_text)
    f.close()
