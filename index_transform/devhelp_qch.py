#!/usr/bin/env python3

#   Copyright (C) 2017  Giedrius Zitkus <elink@namusauga.lt>
#   Copyright (C) 2018  Monika Kairaityte <monika@kibit.lt>
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

from lxml import etree


def convert_toc_lines(source_line, in_section):
    for el_sub in source_line.getchildren():
        el_section_1 = etree.SubElement(in_section, 'section')
        el_section_1.set('title', el_sub.get('name'))
        el_section_1.set('ref', el_sub.get('link'))

        if el_sub.getchildren() != []:
            convert_toc_lines(el_sub, el_section_1)

    return in_section


def convert_toc(in_root):
    el_toc = etree.Element('toc')
    el_section = etree.SubElement(el_toc, 'section')
    el_section.set('title', in_root.get('title'))
    el_section.set('ref', in_root.get('link'))

    chapters_el = in_root[0]
    if chapters_el.tag != '{http://www.devhelp.net/book}chapters':
        raise Exception('Unexpected input document structure')

    convert_toc_lines(chapters_el, el_section)
    return el_toc


def convert_keywords(in_root_k):
    el_keywords = etree.Element('keywords')

    functions_el = in_root_k[1]
    if functions_el.tag != '{http://www.devhelp.net/book}functions':
        raise Exception('Unexpected input document structure')

    for el_function in functions_el:
        el_keyword = etree.SubElement(el_keywords, 'keyword')
        el_keyword.set('name', el_function.get('name'))
        el_keyword.set('id', el_function.get('name'))
        el_keyword.set('ref', el_function.get('link'))

        if el_function.get('name').startswith('std::'):
            el_keyword = etree.SubElement(el_keywords, 'keyword')
            el_keyword.set('name', el_function.get('name'))

            # Add an additional id for libc++ users
            name_without_std = el_function.get('name')[5:]

            el_keyword.set('id', 'std::__LIBCPP_ABI_VERSION::' +
                           name_without_std)
            el_keyword.set('ref', el_function.get('link'))

            el_keyword = etree.SubElement(el_keywords, 'keyword')
            el_keyword.set('name', el_function.get('name'))
            el_keyword.set('id', 'std::__1::' + name_without_std)
            el_keyword.set('ref', el_function.get('link'))

    return el_keywords


# Adds files list from external library
def add_files_list(files_root_f):
    el_files = etree.Element('files')
    for file_item in files_root_f:
        el_file = etree.SubElement(el_files, 'file')
        el_file.text = file_item.text
    return el_files


def convert_devhelp_to_qch(in_root, files_root, virtual_folder):
    out_root = etree.Element('QtHelpProject')
    out_root.set('version', "1.0")
    el = etree.SubElement(out_root, 'namespace')
    el.text = 'cppreference.com.' + in_root.get('name')

    el = etree.SubElement(out_root, 'virtualFolder')
    el.text = virtual_folder

    el = etree.SubElement(out_root, 'customFilter')
    el.set('name', in_root.get('title'))
    el_filter = etree.SubElement(el, 'filterAttribute')
    el_filter.text = in_root.get('name')

    el = etree.SubElement(out_root, 'filterSection')
    el_filter = etree.SubElement(el, 'filterAttribute')
    el_filter.text = in_root.get('name')
    el.append(convert_toc(in_root))
    el.append(convert_keywords(in_root))
    el.append(add_files_list(files_root))

    return etree.tostring(out_root, encoding="utf-8", pretty_print=True,
                          xml_declaration=True)
