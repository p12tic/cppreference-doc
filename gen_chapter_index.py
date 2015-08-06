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

# Generate the chapter index

import argparse
from lxml import etree
from bs4 import BeautifulSoup
import re

def main():
    parser = argparse.ArgumentParser(description='Generate the chapter index')
    parser.add_argument('--i', help='source file', required=True)
    parser.add_argument('--o', help='output file', required=True)

    args = parser.parse_args()

    with open(args.i, 'r') as f:
        soup = BeautifulSoup(f.read(), "lxml")

    root = etree.XML('''<chapters xmlns="http://www.devhelp.net/book"/>''')
    for p in soup.find_all('p'):
        for tag in p:
            if tag.name == "b":
                try:
                    last = etree.SubElement(root, "sub")
                    last.attrib["name"] = re.sub(r"\s+", ' ', tag.a.text.strip())
                    last.attrib["link"] = "en/" + tag.a["href"]
                except KeyError:
                    pass
            if tag.name == "a":
                try:
                    child = etree.SubElement(last, "sub")
                    child.attrib["name"] = re.sub(r"\s+", ' ', tag.text.strip())
                    child.attrib["link"] = "en/" + tag["href"]
                except KeyError:
                    pass

    etree.ElementTree(root).write(args.o, pretty_print=True, encoding='utf-8')


if __name__ == "__main__":
    main()
