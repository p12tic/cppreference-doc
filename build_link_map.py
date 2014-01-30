#!/usr/bin/env python3

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

# This file examines all html files in the output directory and writes
# filename -> title mapping to a xml file.

import fnmatch
import lxml.etree as e
import re
import os

# returns a dict { title -> filename }.
# directory - either 'output/reference' or 'reference'
def build_link_map(directory):
    # find all html files
    html_files = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, '*.html'):
            html_files.append(os.path.join(root, filename))

    link_map = {}

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

        target = os.path.relpath(os.path.abspath(fn), os.path.abspath(directory))
        link_map[title] = target
    return link_map

def main():
    link_map = build_link_map('output/reference')

    # create an xml file containing mapping between page title and actual location
    root = e.Element('files')

    for key in link_map:
        file_el = e.SubElement(root, 'file')
        file_el.set('from', key)
        file_el.set('to', link_map[key])

    out = open('output/link-map.xml', 'w')
    out.write('<?xml version="1.0" encoding="UTF-8"?>')
    out.write(e.tostring(root, encoding=str, pretty_print=True))
    out.close()

if __name__ == "__main__":
    main()
