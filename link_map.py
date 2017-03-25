#!/usr/bin/env python3
'''
    Copyright (C) 2012-2014  Povilas Kanapickas <povilas@radix.lt>

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

class LinkMap:
    def __init__(self):
        self.mapping = dict()

    def read(self, fn):
        root = e.parse(fn)
        el_files = root.xpath('/files/*')

        self.mapping = dict()

        for el_file in el_files:
            fn_from = el_file.get('from')
            fn_to = el_file.get('to')
            self.mapping[fn_from] = fn_to

    def write(self, fn):
        root = e.Element('files')

        for key in self.mapping:
            file_el = e.SubElement(root, 'file')
            file_el.set('from', key)
            file_el.set('to', self.mapping[key])

        out = open(fn, 'w', encoding='utf-8')
        out.write('<?xml version="1.0" encoding="UTF-8"?>')
        out.write(e.tostring(root, encoding=str, pretty_print=True))
        out.close()

    # Returns None on failure
    def get_dest(self, target):
        if target in self.mapping:
            return self.mapping[target]
        return None

    def add_link(self, title, target):
        self.mapping[title] = target
