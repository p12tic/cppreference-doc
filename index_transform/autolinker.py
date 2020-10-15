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
    tags = ['const', 'function', 'class', 'enum', 'variable']
    return el.tag in tags


class Index2AutolinkerGroups(IndexTransform):

    def __init__(self):
        super().__init__(ignore_typedefs=True)
        self.groups = {}
        self.curr_group = None

    def process_item_hook(self, el, full_name, full_link):
        if is_group(el):
            saved_group = self.curr_group

            self.groups[full_name] = {
                'name': full_name,
                'base_url': full_link,
                'urls': ['']
            }
            self.curr_group = full_name
            IndexTransform.process_item_hook(self, el, full_name, full_link)
            self.curr_group = saved_group
        else:
            IndexTransform.process_item_hook(self, el, full_name, full_link)

        if is_group(el.getparent()):
            base_url = self.groups[self.curr_group]['base_url']
            if full_link.find(base_url) == 0:
                rel_link = full_link[len(base_url):]
                if rel_link not in self.groups[self.curr_group]['urls']:
                    self.groups[self.curr_group]['urls'].append(rel_link)
            # else: an error has occurred somewhere - ignore


class Index2AutolinkerLinks(IndexTransform):

    def __init__(self):
        super().__init__()
        self.links = []
        self.curr_group = None

    def process_item_hook(self, el, full_name, full_link):
        self.links.append({'string': full_name, 'target': full_link})

        if is_group(el):
            saved_group = self.curr_group
            self.curr_group = full_name
            IndexTransform.process_item_hook(self, el, full_name, full_link)
            self.curr_group = saved_group
        else:
            IndexTransform.process_item_hook(self, el, full_name, full_link)

        if is_group(el.getparent()) and self.curr_group and \
                needs_entry_in_group(el):

            self.links.append({
                'string': get_rel_name(full_name),
                'target': full_link,
                'on_group': self.curr_group
            })
