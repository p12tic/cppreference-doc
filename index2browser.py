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

if len(sys.argv) != 3:
    print ('''Please provide the file name of the index as the first argument
 and the file name of the destination as the second ''')
    sys.exit(1)

out_f = open(sys.argv[2], 'w', encoding='utf-8')

class Index2Browser(IndexTransform):

    def output_item(self, el, full_name, full_link):
        mark = ''
        if el.tag == 'const': mark = '(const)'
        elif el.tag == 'function': mark = '(function)'
        elif el.tag == 'constructor': mark = '(function)'
        elif el.tag == 'destructor': mark = '(function)'
        elif el.tag == 'class': mark = '(class)'
        elif el.tag == 'enum': mark = '(enum)'
        elif el.tag == 'variable': mark = '(variable)'
        elif el.tag == 'typedef': mark = '(typedef)'
        elif el.tag == 'specialization': mark = '(class)'
        elif el.tag == 'overload': mark = '(function)'

        res = u''
        res += '<tt><b>' + xml_escape(full_name) + '</b></tt> [<span class="link">'
        res += '<a href="http://en.cppreference.com/w/' + xml_escape(full_link) + '">'
        res += full_link + '</a></span>] <span class="mark">' + mark + '</span>\n'
        return res

    def process_item_hook(self, el, full_name, full_link):
        global out_f
        out_f.write('<li>' + self.output_item(el, full_name, full_link) + '<ul>')
        IndexTransform.process_item_hook(self, el, full_name, full_link)
        out_f.write('</ul></li>\n')

out_f.write('''
<html>
  <head>
  <style type="text/css">
    body {
      font-size: 0.8em;
    }

    .link a {
      font-size: 0.8em;
      color: #808080;
    }
    .mark {
      font-size: 0.8em;
      color: #008000;
    }
  </style>
  </head>
  <body>
    <ul>
''')

tr = Index2Browser()
tr.transform(sys.argv[1])

out_f.write('''
    </ul>
  </body>
</html>
''')



