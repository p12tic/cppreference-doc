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
import sys

if len(sys.argv) != 3:
    print ('''Please provide the file name of the index as the first argument
 and the file name of the destination as the second ''')
    sys.exit(1)

out_f = open(sys.argv[2], 'w', encoding='utf-8')

class Index2Highlight(IndexTransform):

    def check_is_member(self, el):
        if el.getparent().tag == 'index':
            return False
        if el.tag == 'function': return True
        elif el.tag == 'variable': return True
        elif el.tag == 'constructor': return True
        elif el.tag == 'destructor': return True
        return False

    def process_item_hook(self, el, full_name, full_link):
        global out_f

        is_member = False
        if self.check_is_member(el): pass
        elif '<' in full_name: pass
        elif '>' in full_name: pass
        elif '(' in full_name: pass
        elif ')' in full_name: pass
        else:
            out_f.write(full_name + ' => ' + full_link + '\n')

        IndexTransform.process_item_hook(self, el, full_name, full_link)

    def inherits_worker(self, parent_name, pending, finished=list()):
        pass # do not walk the inheritance hierarchy

tr = Index2Highlight()
tr.transform(sys.argv[1])



