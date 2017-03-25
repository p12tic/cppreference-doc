#!/usr/bin/env python3
'''
    Copyright (C) 2012-2013  Povilas Kanapickas <povilas@radix.lt>

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

import lxml.etree as e
from link_map import LinkMap
import sys

if len(sys.argv) != 3:
    print('''Please provide the following 2 argument:
 * the file name of the source file
 * the file name of the destination file
''')

in_fn = sys.argv[1]
out_fn = sys.argv[2]

mapping = LinkMap()
mapping.read('output/link-map.xml')

root = e.parse(in_fn)

el_mod = root.xpath('//*[@link]')
for el in el_mod:
    link = el.get('link')
    target = mapping.get_dest(link)
    if target == None:
        print('Could not find ' + link + ' in mapping')
        target = '404'
    el.set('link', target)

out_f = open(out_fn, 'w', encoding='utf-8')
out_f.write(e.tostring(root, encoding='unicode', pretty_print=True))
out_f.close()

