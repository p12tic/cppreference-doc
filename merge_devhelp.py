#!/usr/bin/env python3

#   Copyright (C) 2015  Michael Munzert <info@mm-log.com>
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

# Merge the c and the cpp devhelp files

import argparse
from lxml import etree
from copy import deepcopy
import datetime

def main():
    parser = argparse.ArgumentParser(description='Merge the c and the cpp devhelp files')
    parser.add_argument('--c', help='devhelp file for c', required=True)
    parser.add_argument('--cpp', help='devhelp file for c++', required=True)
    parser.add_argument('--out', help='output file', required=True)

    args = parser.parse_args()

    with open(args.c, 'r') as f:
        doc_c = etree.XML(f.read())

    with open(args.cpp, 'r') as f:
        doc_cpp = etree.XML(f.read())


    timestamp = datetime.datetime.now().strftime('%Y-%m-%d')

    root = etree.XML('''<book xmlns="http://www.devhelp.net/book" title="C/C++ Standard Library reference" name="{}" base="/usr/share/cppreference/doc/html" link="en/index.html" version="2" language="c/c++"></book>'''.format(timestamp))

    chapters = etree.SubElement(root, "chapters")
    chapters.attrib["xmlns"] = "http://www.devhelp.net/book"

    node_c = etree.SubElement(chapters, "sub")
    node_c.attrib["name"] = "C"
    node_c.attrib["link"] = "en/c.html"

    node_cpp = etree.SubElement(chapters, "sub")
    node_cpp.attrib["name"] = "C++"
    node_cpp.attrib["link"] = "en/cpp.html"

    node_fct = etree.SubElement(root, "functions")

    ns = doc_c.nsmap[None]
    chapters_c = doc_c.find(".//{" + ns + "}chapters")
    for element in chapters_c:
        temp = deepcopy(element)
        temp.text = None
        node_c.append(temp)

    ns = doc_cpp.nsmap[None]
    chapters_cpp = doc_cpp.find(".//{" + ns + "}chapters")
    for element in chapters_cpp:
        temp = deepcopy(element)
        temp.text = None
        node_cpp.append(temp)

    for element in doc_c.find(".//{" + ns + "}functions"):
        temp = deepcopy(element)
        try:
            temp.attrib["link"] = "en/" + temp.attrib["link"] + ".html"
        except KeyError:
            pass
        node_fct.append(temp)

    for element in doc_cpp.find(".//{" + ns + "}functions"):
        temp = deepcopy(element)
        try:
            temp.attrib["link"] = "en/" + temp.attrib["link"] + ".html"
        except KeyError:
            pass
        node_fct.append(temp)

    etree.ElementTree(root).write(args.out, pretty_print=True, encoding='utf-8')

if __name__ == "__main__":
    main()
