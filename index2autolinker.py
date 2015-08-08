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

''' This script produces a definition file for AutoLinker extension

    The definitions are written in JSON in the following format:

    {
        "groups" : [
            {
                name : "string",
                OPTIONAL base_url : "string", END
                urls : [ "url", "url", ... ],
            },
            ...
        ],
        "links" : [
            {
                string : "string",
                EITHER on_group : "name" OR on_page : "url" END
                target : "url",
            },
            ...
        ],
    }
'''

import sys
import json

from index_transform import IndexTransform
from xml_utils import xml_escape

if len(sys.argv) != 3:
    print('''Please provide the file name of the index as the first argument
 and the file name of the destination as the second ''')
    sys.exit(1)

out_f = open(sys.argv[2], 'w')

groups = {}
links = []

def get_rel_name(full_name):
    pos = full_name.rfind("::")
    return full_name[pos+2:]


def is_group(el):
    curr_el = el
    while True:
        if curr_el.tag != 'class' and curr_el.tag != 'enum':
            return False
        curr_el = curr_el.getparent()
        if curr_el.tag == 'index':
            return True

def needs_entry_in_group(el):
    if el.tag == 'const': return True
    if el.tag == 'function': return True
    if el.tag == 'class': return True
    if el.tag == 'enum': return True
    if el.tag == 'variable': return True
    return False

class Index2AutolinkerGroups(IndexTransform):

    def __init__(self):
        super(Index2AutolinkerGroups, self).__init__(ignore_typedefs = True)
        self.curr_group = None

    def process_item_hook(self, el, full_name, full_link):
        global groups
        if is_group(el):
            saved_group = self.curr_group

            groups[full_name] = {
                'name' : full_name,
                'base_url' : full_link,
                'urls' : ['']
            }
            self.curr_group = full_name
            IndexTransform.process_item_hook(self, el, full_name, full_link)
            self.curr_group = saved_group
        else:
            IndexTransform.process_item_hook(self, el, full_name, full_link)

        if is_group(el.getparent()):
            base_url = groups[self.curr_group]['base_url']
            if full_link.find(base_url) == 0:
                rel_link = full_link[len(base_url):]
                if not rel_link in groups[self.curr_group]['urls']:
                    groups[self.curr_group]['urls'].append(rel_link)
            # else: an error has occurred somewhere - ignore

class Index2AutolinkerLinks(IndexTransform):

    def __init__(self):
        super(Index2AutolinkerLinks, self).__init__()
        self.curr_group = None

    def process_item_hook(self, el, full_name, full_link):
        global links
        links.append({ 'string' : full_name, 'target' : full_link })

        if is_group(el):
            saved_group = self.curr_group
            self.curr_group = full_name
            IndexTransform.process_item_hook(self, el, full_name, full_link)
            self.curr_group = saved_group
        else:
            IndexTransform.process_item_hook(self, el, full_name, full_link)

        if is_group(el.getparent()) and self.curr_group and needs_entry_in_group(el):

            links.append({ 'string' : get_rel_name(full_name),
                           'target' : full_link,
                           'on_group' : self.curr_group
                         })



tr = Index2AutolinkerGroups()
tr.transform(sys.argv[1])

tr = Index2AutolinkerLinks()
tr.transform(sys.argv[1])

json_groups = [ v for v in groups.values() ]

json_groups = sorted(json_groups, key=lambda x: x['name'])
links = sorted(links, key=lambda x: x['target'])

out_f.write(json.dumps({ 'groups' : json_groups, 'links' : links}, indent=None,
                       separators=(',\n', ': '), sort_keys=True))
out_f.close()
