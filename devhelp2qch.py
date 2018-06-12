#!/usr/bin/env python3

#   Copyright (C) 2017  Giedrius Zitkus <elink@namusauga.lt>
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

# devhelp2qch.py script converts 'in_root' xml source file to 'out_root' xml output
# including files list from library 'files_root' at the end.

from lxml import etree
from copy import deepcopy
import sys
import argparse

def convert_toc_lines(source_line, in_section):
    i = 0
    for el_sub in source_line.getchildren():
        el_section_1 = etree.XML('<section/>')
        el_section_1.set('title', el_sub.get('name'))
        el_section_1.set('ref', el_sub.get('link'))

        if el_sub.getchildren() != []:
            in_section.append(convert_toc_lines(el_sub, el_section_1))
        else:
            in_section.append(el_section_1)

    return in_section

def convert_toc(in_root_t):
    el_toc = etree.XML('<toc/>')
    el_section = etree.XML('<section/>')
    el_section.set('title', in_root_t.get('title'))
    el_section.set('ref', in_root_t.get('link'))

    chapters_el = in_root_t[0]
    if chapters_el.tag != '{http://www.devhelp.net/book}chapters':
        raise Exception('Unexpected input document structure')

    el_toc.append(convert_toc_lines(chapters_el, el_section))
    return el_toc

def convert_keywords(in_root_k):
    el_keywords = etree.XML('<keywords/>')

    functions_el = in_root_k[1]
    if functions_el.tag != '{http://www.devhelp.net/book}functions':
        raise Exception('Unexpected input document structure')

    for el_function in functions_el:
        el_keyword = etree.XML('<keyword/>')
        el_keyword.set('name', el_function.get('name'))
        el_keyword.set('id', el_function.get('name'))
        el_keyword.set('ref', el_function.get('link'))

        el_keywords.append(el_keyword)
        if el_function.get('name').startswith('std::'):
            el_keyword = etree.XML('<keyword/>')
            el_keyword.set('name', el_function.get('name'))

            # Add an additional id for libc++ users
            name_without_std = el_function.get('name')[5:]

            el_keyword.set('id', 'std::__LIBCPP_ABI_VERSION::' + name_without_std)
            el_keyword.set('ref', el_function.get('link'))

            el_keywords.append(el_keyword)

            el_keyword = etree.XML('<keyword/>')
            el_keyword.set('name', el_function.get('name'))
            el_keyword.set('id', 'std::__1::' + name_without_std)
            el_keyword.set('ref', el_function.get('link'))

            el_keywords.append(el_keyword)
    return el_keywords

# Adds files list from external library
def add_files_list(files_root_f):
    el_files = etree.XML('<files/>')
    for file_item in files_root_f:
        el_file = etree.XML('<file/>')
        el_file.text = file_item.text
        el_files.append(el_file)
    return el_files

def convert_devhelp_to_qch(in_root, files_root, out_root, virtual_folder):
    el = etree.XML('<namespace/>')
    el.text = 'cppreference.com.' + in_root.get('name')
    out_root.append(el)

    el = etree.XML('<virtualFolder/>')
    el.text = virtual_folder
    out_root.append(el)

    el = etree.XML('<customFilter/>')
    el.set('name', in_root.get('title'))
    el_filter = etree.XML('<filterAttribute/>')
    el_filter.text = in_root.get('name')
    el.append(el_filter)
    out_root.append(el)

    el = etree.XML('<filterSection/>')
    el_filter = etree.XML('<filterAttribute/>')
    el_filter.text = in_root.get('name')
    el.append(el_filter)
    el.append(convert_toc(in_root))
    el.append(convert_keywords(in_root))
    el.append(add_files_list(files_root))
    out_root.append(el)

def main():
    parser = argparse.ArgumentParser(prog='devhelp2qch.py')
    parser.add_argument('--src', type=str, help='The path to the XML input file')
    parser.add_argument('--dst', type=str, help='The path to the destination XML file')
    parser.add_argument('--virtual_folder', type=str, help='Virtual folder name')
    parser.add_argument('--file_list', type=str, help='The path to the file list in XML file')
    args = parser.parse_args()

    src_path = args.src
    dst_path = args.dst
    v_folder = args.virtual_folder
    file_path = args.file_list

    parser = etree.XMLParser(encoding='UTF-8', recover=True)
    in_tree = etree.parse(src_path, parser)
    file_tree = etree.parse(file_path, parser)
    out_el = etree.XML('<QtHelpProject xmlns:devhelp="http://www.devhelp.net/book" xmlns:str="http://exslt.org/strings" version="1.0"/>')

    convert_devhelp_to_qch(in_tree.getroot(), file_tree.getroot(), out_el, v_folder)

    out_f = open(dst_path, 'wb')
    out_f.write(etree.tostring(out_el, encoding="utf-8", pretty_print=True, xml_declaration=True))
    out_f.close()

if __name__ == "__main__":
    main()
