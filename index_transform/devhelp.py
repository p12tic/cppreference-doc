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

from index_transform.common import IndexTransform
from xml_utils import xml_escape
from index_transform import *
from lxml import etree
import io

class Index2Devhelp(IndexTransform):

    def __init__(self, functions_el):
        super().__init__()
        self.functions_el = functions_el

    def get_mark(self, el):
        if el.tag == 'const': return 'macro'
        elif el.tag == 'function': return 'function'
        elif el.tag == 'constructor': return 'function'
        elif el.tag == 'destructor': return 'function'
        elif el.tag == 'class': return 'class'
        elif el.tag == 'enum': return 'enum'
        elif el.tag == 'typedef': return 'typedef'
        elif el.tag == 'specialization': return 'class'
        elif el.tag == 'overload': return 'function'
        # devhelp does not support variables in its format
        elif el.tag == 'variable': return ''
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
