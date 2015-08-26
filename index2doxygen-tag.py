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

from index_transform import IndexTransform
from xml_utils import xml_escape
from link_map import LinkMap
from functools import total_ordering
import sys

if len(sys.argv) != 4:
    print ('''Please provide the following 3 arguments:
 * the file name of the link map or 'web' if no link remap should be done
 * the file name of the source file
 * the file name of the destination file
''')
    sys.exit(1)

link_map_fn = sys.argv[1]
in_fn = sys.argv[2]
dest_fn = sys.argv[3]

indent_level_inc = 2

out_f = open(dest_fn, 'w')

link_map = None
if link_map_fn != 'web':
    link_map = LinkMap()
    link_map.read(link_map_fn)

class ItemKind:
    VARIABLE = 0,
    FUNCTION = 1,
    CLASS = 2,
    TYPEDEF = 3,
    NAMESPACE = 4

@total_ordering
class Item:

    def __init__(self):
        self.name = ""
        self.full_name = ""
        self.kind = ItemKind.NAMESPACE
        self.link = ""
        self.members = {}

    def __eq__(self, other):
        return self.full_name == other.full_name

    def __lt__(self, other):
        return self.full_name < other.full_name

ns_map = Item()

def add_to_map(full_name, full_link, item_kind):
    global ns_map
    names = full_name.split('::')
    parsed_names = []
    last_name = names.pop() # i.e. unqualified name
    curr_item = ns_map

    for name in names:
        parsed_names.append(name)
        if name in curr_item.members:
            curr_item = curr_item.members[name]
            if curr_item.kind not in [ ItemKind.CLASS, ItemKind.NAMESPACE ]:
                print("ERROR: " + name + " in " + full_name +
                      " is not a class or namespace")
                return
        else:
            # we add inexistent intermediate elements as namespaces and convert
            # them to classes later when class definitions are encountered
            new_item = Item()
            new_item.name = name
            new_item.full_name = "::".join(parsed_names)
            new_item.kind = ItemKind.NAMESPACE

            curr_item.members[name] = new_item
            curr_item = new_item

    if last_name in curr_item.members:
        curr_item = curr_item.members[last_name]
        if (item_kind == ItemKind.CLASS and
            curr_item.kind in [ ItemKind.CLASS, ItemKind.NAMESPACE ]):
            curr_item.kind = item_kind # fix namespaces that are actually classes
            curr_item.link = full_link
        else:
            print("ERROR: Duplicate element: " + full_name)
    else:
        new_item = Item()
        new_item.full_name = full_name
        new_item.name = last_name
        new_item.link = full_link
        new_item.kind = item_kind
        curr_item.members[last_name] = new_item
        curr_item = new_item
    return

def print_members(out_f, curr_item):
    global link_map
    for item in sorted(curr_item.members.values()):
        if link_map:
            link = link_map.get_dest(item.link)
            if link == None and item.kind != ItemKind.NAMESPACE:
                print("WARN: " + item.full_name + " contains invalid link")
                link = '404'
        else:
            link = item.link

        if item.kind == ItemKind.VARIABLE:
            out_f.write('    <member kind="variable">\n' +
                        '      <type>T</type>\n' +
                        '      <name>' + xml_escape(item.name) + '</name>\n' +
                        '      <anchorfile>' + xml_escape(link) + '</anchorfile>\n' +
                        '      <anchor></anchor>\n' +
                        '      <arglist></arglist>\n' +
                        '    </member>\n')
        elif item.kind == ItemKind.FUNCTION:
            out_f.write('    <member kind="function">\n' +
                        '      <type>T</type>\n' +
                        '      <name>' + xml_escape(item.name) + '</name>\n' +
                        '      <anchorfile>' + xml_escape(link) + '</anchorfile>\n' +
                        '      <anchor></anchor>\n' +
                        '      <arglist>(T... args)</arglist>\n' +
                        '    </member>\n')
        elif item.kind == ItemKind.CLASS:
            out_f.write('    <class kind="class">' + xml_escape(item.full_name) + '</class>\n')
        elif item.kind == ItemKind.NAMESPACE:
            out_f.write('    <namespace>' + xml_escape(item.full_name) + '</namespace>\n')

def print_map_item(out_f, curr_item):
    item_kind_to_attr = { ItemKind.NAMESPACE : 'namespace',
                          ItemKind.CLASS : 'class' }
    if curr_item.kind not in item_kind_to_attr:
        print('ERROR: only namespaces and classes can have members')
        return

    out_f.write('  <compound kind="' + item_kind_to_attr[curr_item.kind] + '">\n' +
                '    <name>' + xml_escape(curr_item.full_name) + '</name>\n' +
                '    <filename>' + xml_escape(curr_item.link) + '</filename>\n')
    print_members(out_f, curr_item)
    out_f.write('  </compound>\n')

    for item in sorted(curr_item.members.values()):
        if item.kind in [ ItemKind.NAMESPACE, ItemKind.CLASS ]:
            print_map_item(out_f, item)

def print_map(out_f, ns_map):
    for item in sorted(ns_map.members.values()):
        if item.kind in [ ItemKind.NAMESPACE, ItemKind.CLASS ]:
            print_map_item(out_f, item)
        else:
            print("WARN: " + item.full_name + " ignored")

class Index2Devhelp(IndexTransform):

    def get_item_kind(self, el):
        if el.tag == 'const': return None
        elif el.tag == 'function': return ItemKind.FUNCTION
        elif el.tag == 'constructor': return ItemKind.FUNCTION
        elif el.tag == 'destructor': return ItemKind.FUNCTION
        elif el.tag == 'class': return ItemKind.CLASS
        elif el.tag == 'enum': return 'enum'
        elif el.tag == 'typedef': return ItemKind.CLASS
        elif el.tag == 'specialization': return None
        elif el.tag == 'overload': return None
        elif el.tag == 'variable': return ItemKind.VARIABLE
        return None

    def process_item_hook(self, el, full_name, full_link):
        item_kind = self.get_item_kind(el)
        if item_kind != None:
            add_to_map(full_name, full_link, item_kind)
        IndexTransform.process_item_hook(self, el, full_name, full_link)

out_f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n')
out_f.write('<tagfile>\n')

tr = Index2Devhelp()
tr.transform(in_fn)
print_map(out_f, ns_map)
out_f.write('''</tagfile>
''')
