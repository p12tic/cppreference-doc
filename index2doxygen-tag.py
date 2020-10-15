#!/usr/bin/env python3
'''
    Copyright (C) 2014  Povilas Kanapickas <povilas@radix.lt>

    This file is part of cppreference-doc

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see http://www.gnu.org/licenses/.
'''

import argparse

from lxml import etree

from index_transform.doxygen_tag import Index2DoxygenTag
from index_transform.doxygen_tag import Item
from index_transform.doxygen_tag import print_map
from link_map import LinkMap


def main():
    parser = argparse.ArgumentParser(prog='index2doxygen-tag')
    parser.add_argument(
        'link_map_fn', type=str,
        help='Path to index file to process')

    parser.add_argument(
        'in_fn', type=str,
        help='the file name of the link map or \'web\' if no link remap '
             'should be done')

    parser.add_argument(
        'chapters_fn', type=str,
        help='the file name of the source file')

    parser.add_argument(
        'dest_fn', type=str,
        help='the file name of the destination file')

    args = parser.parse_args()

    link_map_fn = args.link_map_fn
    in_fn = args.in_fn
    chapters_fn = args.chapters_fn
    dest_fn = args.dest_fn

    out_f = open(dest_fn, 'w', encoding='utf-8')

    link_map = None
    if link_map_fn != 'web':
        link_map = LinkMap()
        link_map.read(link_map_fn)

    ns_map = Item()

    out_f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n')
    out_f.write('<tagfile>\n')

    with open(chapters_fn, encoding='utf-8') as chapters_f:
        chapters_tree = etree.parse(chapters_f)
        for header_chapter in \
                chapters_tree.getroot().findall(".//*[@name='Headers']/*"):
            out_f.write('  <compound kind="file">\n')
            out_f.write('    <name>{0}</name>\n'.format(
                header_chapter.attrib['name']))
            out_f.write('    <filename>{0}</filename>\n'.format(
                header_chapter.attrib['link']))
            out_f.write('    <namespace>std</namespace>\n')
            out_f.write('  </compound>\n')

    tr = Index2DoxygenTag(ns_map)
    tr.transform_file(in_fn)
    print_map(out_f, link_map, ns_map)
    out_f.write('''</tagfile>
''')


if __name__ == '__main__':
    main()
