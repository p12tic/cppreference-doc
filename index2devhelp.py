#!/usr/bin/env python3
'''
    Copyright (C) 2013  Povilas Kanapickas <povilas@radix.lt>

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

from index_transform import IndexTransform
from xml_utils import xml_escape
import sys

if len(sys.argv) != 8:
    print ('''Please provide the following 7 arguments:
 * a link to the location of the book
 * the chapters file to include
 * the title of the book
 * the name of the package
 * the link relative to the root of the documentation
 * the file name of the source file
 * the file name of the destination file
''')

book_base = sys.argv[1]
chapters_fn = sys.argv[2]
book_title = sys.argv[3]
book_name = sys.argv[4]
rel_link = sys.argv[5]
in_fn = sys.argv[6]
dest_fn = sys.argv[7]

out_f = open(dest_fn, 'w', encoding='utf-8')


class Index2Devhelp(IndexTransform):

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
        global out_f
        out_f.write('<keyword type="' + xml_escape(self.get_mark(el))
                    + '" name="' + xml_escape(full_name)
                    + '" link="' + xml_escape(full_link) + '"/>\n')
        IndexTransform.process_item_hook(self, el, full_name, full_link)

out_f.write('<?xml version="1.0"?>\n'
           + '<book title="' + xml_escape(book_title)
           + '" xmlns="http://www.devhelp.net/book'
           + '" name="' + xml_escape(book_name)
           + '" base="' + xml_escape(book_base)
           + '" link="' + xml_escape(rel_link)
           + '" version="2" language="c++">\n')

chapters_f = open(chapters_fn, encoding='utf-8')
out_f.write(chapters_f.read() + '\n')
out_f.write('<functions>')

tr = Index2Devhelp()
tr.transform(in_fn)

out_f.write('''
  </functions>
</book>
''')
