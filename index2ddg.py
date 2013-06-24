#!/usr/bin/env python3
'''
    Copyright (C) 2013  p12 <tir5c3@yahoo.co.uk>

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

import sys, json, os, sys, re, fnmatch
import lxml.etree as e
import lxml.html as html

from index_transform import IndexTransform, xml_escape
from build_link_map import build_link_map
from ddg_parse_html import get_declaration, get_short_description, DdgException

if len(sys.argv) != 3 and not (sys.arg > 2 and sys.argv[1] == 'debug'):
    print('''Please provide the file name of the index as the first argument
 and the file name of the output as the second ''')
    sys.exit(1)

# If a the second argument is 'debug', the program switches to debug mode and
# prints everything to stdout. If the third argument is provided, the program
# processes only the identifiers that match the provided string

debug = False
debug_ident = None
if len(sys.argv) > 2 and sys.argv[2] == 'debug':
    debug = True
    if len(sys.argv) > 3:
        debug_ident = sys.argv[3]

index_file = sys.argv[1]
output_file = sys.argv[2]

items = {}

# Entry types
# class or struct
ITEM_TYPE_CLASS = 1

# member function or free function
ITEM_TYPE_FUNCTION = 2

# member function that is described in the same page as the class
ITEM_TYPE_FUNCTION_INLINEMEM = 3

# enum
ITEM_TYPE_ENUM = 4

# a value of enum
ITEM_TYPE_ENUM_CONST = 5

def get_item_type(el):
    if (el.tag == 'const' and el.getparent().tag == 'enum' and
        el.get('link') == '.'):
        return ITEM_TYPE_ENUM_CONST
    if el.tag == 'function':
        if el.get('link') == '.':
            return ITEM_TYPE_FUNCTION_INLINEMEM
        else:
            return ITEM_TYPE_FUNCTION
    if el.tag == 'class':
        return ITEM_TYPE_CLASS
    if el.tag == 'enum':
        return ITEM_TYPE_ENUM
    return None # not recognized

class Index2DuckDuckGoList(IndexTransform):

    def __init__(self):
        super(Index2DuckDuckGoList, self).__init__(ignore_typedefs=True)

    def process_item_hook(self, el, full_name, full_link):
        global items

        item_type = get_item_type(el)
        if item_type:
            if full_link in items:
                items[full_link][full_name] = item_type
            else:
                items[full_link] = { full_name : item_type }
        IndexTransform.process_item_hook(self, el, full_name, full_link)

# get a list of pages to analyze
tr = Index2DuckDuckGoList()
tr.transform(index_file)

# get a list of existing pages
html_files = []
for root, dirnames, filenames in os.walk('reference'):
    for filename in fnmatch.filter(filenames, '*.html'):
        html_files.append(os.path.join(root, filename))

# get a mapping between titles and pages

# linkmap = dict { title -> filename }
link_map = build_link_map('reference')

# create a list of processing instructions for each page
proc_ins = {}

for link in items:
    if link in link_map:
        page = link_map[link]
        if page not in proc_ins:
            proc_ins[page] = { 'link': link, 'ident': {}}
        for ident in items[link]:
            proc_ins[page]['ident'][ident] = items[link][ident]

# process the files

# returns the unqualified name of an identifier
def get_name(ident):
    if ident.find('(') != -1:
        ident = re.sub('\(.*?\)', '', ident)
    if ident.find('<') != -1:
        ident = re.sub('\<.*?\>', '', ident)
    qpos = ident.rfind('::')
    if qpos != -1:
        ident = ident[qpos+2:]
    return ident


if debug:
    out = sys.stdout
else:
    out = open(output_file, 'w')

#i=1
for page in proc_ins:
    identifiers = proc_ins[page]['ident']
    link = proc_ins[page]['link']

    if debug_ident:
        ignore = False
        for ident in identifiers:
            if ident.find(debug_ident) == -1:
                ignore = True
                break
        if ignore:
            continue

    #print(str(i) + '/' + str(len(proc_ins)) + ': ' + link)
    #i+=1

    root = e.parse('reference/'+page, parser=html.HTMLParser())

    for item_ident in identifiers:

        item_type = identifiers[item_ident]

        # get the name by extracting the unqualified identifier
        name = get_name(item_ident)

        try:
            if item_type == ITEM_TYPE_CLASS:

                code,version,multi = get_declaration(root, name)
                if multi:
                    code += '\n...'
                desc = get_short_description(root, version)

                abstract = '<code>' + code + '</code><br/>' + desc

            elif item_type == ITEM_TYPE_FUNCTION:

                code,version,multi = get_declaration(root, name)
                if multi:
                    code += '\n...'
                desc = get_short_description(root, version)

                abstract = '<code>' + code + '</code><br/>' + desc


            elif item_type == ITEM_TYPE_FUNCTION_INLINEMEM:
                raise DdgException("INLINEMEM")
                ''' (see versioned declarations, picking up the text)
                    declaration is selected from the member table
                    the member table is found according to the identifier (last part after :: is enough, hopefully
                '''

            elif item_type == ITEM_TYPE_ENUM:
                raise DdgException("ENUM")
                ''' (see versioned declarations, picking up the text) '''

            elif item_type == ITEM_TYPE_ENUM_CONST:
                raise DdgException("ENUM_CONST")
                ''' search for the const -> definition table before the first heading
                    search for const in code, pick the definition either:
                        within enum declaration, result in ... const ...
                        external enum, the declaration is since the last punctuation till the ';', ',', etc
                '''

            # title
            line = 'c++ ' + item_ident + '\t'
            # type
            line += 'A\t'
            # redirect, otheruses, categories, references, see_also,
            # further_reading, external links, disambiguation, images
            line += '\t\t\t\t\t\t\t\t\t'
            # abstract
            abstract = abstract.replace('\n','\\\\n')
            line += abstract + '\t'
            # source url
            line += '[http://en.cppreference.com/w/' + link + ' Cppreference]\n'
            out.write(line)
        except DdgException as err:
            if debug:
                line = '# error (' + str(err) + "): " + link + ": " + item_ident + "\n"
                out.write(line)
