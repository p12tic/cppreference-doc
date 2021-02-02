'''
    Copyright (C) 2013  Povilas Kanapickas <povilas@radix.lt>
    Copyright (C) 2018  Monika Kairaityte <monika@kibit.lt>

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

from lxml import etree

from index_transform.common import IndexTransform


class Index2Devhelp(IndexTransform):

    def __init__(self, functions_el):
        super().__init__()
        self.functions_el = functions_el

    def get_mark(self, el):
        tag_to_mark = {
            'const': 'macro',
            'function': 'function',
            'constructor': 'function',
            'destructor': 'function',
            'class': 'class',
            'enum': 'enum',
            'typedef': 'typedef',
            'specialization': 'class',
            'overload': 'function',
            # devhelp does not support variables in its format
            'variable': ''
        }

        if el.tag in tag_to_mark:
            return tag_to_mark[el.tag]

        return ''

    def process_item_hook(self, el, full_name, full_link):
        keyword_el = etree.SubElement(self.functions_el, 'keyword')
        keyword_el.set('type', self.get_mark(el))
        keyword_el.set('name', full_name)
        keyword_el.set('link', full_link)

        IndexTransform.process_item_hook(self, el, full_name, full_link)


def transform_devhelp(book_title, book_name, book_base, rel_link, chapters_fn,
                      in_fn):
    root_el = etree.Element('book')
    root_el.set('xmlns', 'http://www.devhelp.net/book')
    root_el.set('title', book_title)
    root_el.set('name', book_name)
    root_el.set('base', book_base)
    root_el.set('link', rel_link)
    root_el.set('version', '2')
    root_el.set('language', 'c++')

    chapters_tree = etree.parse(chapters_fn)
    root_el.append(chapters_tree.getroot())

    functions_el = etree.SubElement(root_el, 'functions')

    tr = Index2Devhelp(functions_el)
    tr.transform_file(in_fn)

    return etree.tostring(root_el, pretty_print=True, xml_declaration=True,
                          encoding='utf-8')
