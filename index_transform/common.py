#!/usr/bin/env python3
'''
    Copyright (C) 2011-2013  Povilas Kanapickas <povilas@radix.lt>

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

'''
    This is a python script for various transformations of the index.

    Concrete transformations can be implemented by subclassing IndexTransform
    and overriding the provided hooks.

    process_item_hook:

    Called to output information of a feature and continue the processing of the
    children. By default just processes the children.
'''

import lxml.etree as e
import re

class IndexTransform:

    def __init__(self, ignore_typedefs=False, ignore_inherits=False):
        self.ignore_typedefs = ignore_typedefs
        self.ignore_inherits = ignore_inherits

    """ Returns the attribute 'attr' of 'el', raises exception on error
    """
    def get_attr(self, el, attr):
        a = el.get(attr)
        if not a:
            nm = el.get('name')
            if nm:
                nm_str = '( name: ' + nm + ' )'
            else:
                nm_str = ''
            raise Exception('Element \'' + el.tag + '\' does not have attribute \'' +
                             attr + '\' ' + nm_str)
        return str(a)

    """ Returns the relative link of 'el' to its parent, if any
    """
    def get_link(self, el, default = None):
        if not default:
            default = self.get_name(el)

        link = el.get('link')
        if link == None:
            return default
        if link == '.':
            return ''
        return str(link)

    """ Appends two possible empty relative links
    """
    def link_append(self, el, link, parent_link):
        if parent_link != '' and link != '':
            return parent_link + '/' + link
        return parent_link + link

    """ Returns the absolute link of el
    """
    def get_full_link(self, el, parent_link):

        if el.tag == 'typedef':
            alias_name = el.get('alias')
            if alias_name:
                return self.get_link(self.get_alias(el, alias_name))
            else:
                return self.link_append(el, self.get_link(el), parent_link)

        elif el.tag == 'constructor':
            d_link = parent_link.split('/')[-1]
            return self.link_append(el, self.get_link(el, default=d_link), parent_link)

        elif el.tag == 'destructor':
            d_link = '~' + parent_link.split('/')[-1]
            return self.link_append(el, self.get_link(el, default=d_link), parent_link)

        else:
            return self.link_append(el, self.get_link(el), parent_link)

    """ Returns the name of el """
    def get_name(self, el):
        return self.get_attr(el, 'name')

    """ Returns the full name (with the namespace qualification) of el """
    def get_full_name(self, el, parent_name):
        if not parent_name and el.tag in ['constructor', 'destructor',
                                          'overload', 'specialization']:
            raise Exception('element \'' + el.tag + '\' does not have a parent')

        if el.tag == 'constructor':
            return parent_name + '::' + parent_name.split('::')[-1]
        if el.tag == 'destructor':
            return parent_name + '::~' + parent_name.split('::')[-1]
        elif el.tag == 'specialization':
            return self.get_name(el) + '<' + parent_name + '>'
        elif el.tag == 'overload':
            return self.get_name(el) + '(' + parent_name + ')'
        else:
            name = ''
            if parent_name:
                name += parent_name + '::'
            name += self.get_name(el)
            return name

    """ Returns the element within the document that has a name that matches
        'name'
    """
    def get_alias(self, el, name):
        aliases = el.xpath('/index/class[@name = \'' + name + '\'] |' +
                            '/index/enum[@name = \'' + name + '\']')
        if len(aliases) == 0:
            raise Exception('No aliases found for \'' + name + '\'')
        if len(aliases) > 1:
            raise Exception('More than one alias found for \'' + name + '\'')
        return aliases[0]

    """ Processes one item """
    def process_item(self, el, parent_name, parent_link):
        if el.tag in ['const','function','class','enum','variable','typedef',
                      'constructor','destructor','specialization','overload']:

            full_name = self.get_full_name(el, parent_name)
            full_link = self.get_full_link(el, parent_link)

            self.process_item_hook(el, full_name, full_link)

        elif el.tag == 'inherits' and el.getparent().xpath('child::inherits')[0] == el:
            if self.ignore_inherits:
                return
            pending = el.getparent().xpath('child::inherits')
            self.inherits_worker(parent_name, pending, list())

    """ Processes children of an item """
    def process_children(self, el, parent_name, parent_link):

        if el.tag == 'class' or el.tag == 'enum':
            for child in el:
                self.process_item(child, parent_name, parent_link)
        elif el.tag == 'typedef':
            if self.ignore_typedefs:
                return

            alias_name = el.get('alias')
            if alias_name:
                target = self.get_alias(el, alias_name)
            else:
                return
            link = self.get_link(target)
            for target_ch in target:
                self.process_item(target_ch, parent_name, link)

    """ Pulls the contents of the inherited classes. Diamond inheritance is
        handled properly
    """
    def inherits_worker(self, parent_name, pending, finished):
        if len(pending) == 0:
            return

        current = pending.pop(0)

        # find the source class/enum
        source = self.get_alias(current, self.get_attr(current, 'name'))

        if not source in finished:
            finished.append(source)
            parent_link = self.get_attr(source, 'link')
            for source_ch in source:
                ignore_tags =  ['constructor', 'destructor', 'inherits', 'specialization', 'overload']
                if source_ch.tag in ignore_tags: pass
                elif source_ch.tag == 'function' and source_ch.get('name') == 'operator=': pass
                else:
                    self.process_item(source_ch, parent_name, parent_link)

        # append new elements
        more_pending = source.xpath('child::inherits')
        more_pending = [p for p in more_pending if not p is current]
        pending.extend(more_pending)

        self.inherits_worker(parent_name, pending, finished)

    """ Transforms the index """
    def transform(self, fn):
        root = e.parse(fn)
        elems = root.xpath('/index/*')
        for el in elems:
            self.process_item(el, '', '')

    """ Hooks """
    def process_item_hook(self, el, full_name, full_link):
        self.process_children(el, full_name, full_link)
