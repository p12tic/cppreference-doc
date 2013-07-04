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
from ddg_parse_html import get_declarations, get_short_description, DdgException

if len(sys.argv) != 3 and not (len(sys.argv) > 2 and sys.argv[2] == 'debug'):
    print('''Please provide the file name of the index as the first argument
 and the file name of the output as the second ''')
    sys.exit(1)

MAX_CODE_LINES = 6

# If a the second argument is 'debug', the program switches to debug mode and
# prints everything to stdout. If the third argument is provided, the program
# processes only the identifiers that match the provided string

debug = False
debug_ident = None
if len(sys.argv) > 2 and sys.argv[2] == 'debug':
    debug = True
    if len(sys.argv) > 3:
        debug_ident = sys.argv[3]

# track the statistics of number of lines used by the entries
debug_num_lines = [0 for i in range(40)]

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
        fn = link_map[link]
        if fn not in proc_ins:
            proc_ins[fn] = { 'fn': fn, 'link': link, 'idents': {}}
        for ident in items[link]:
            proc_ins[fn]['idents'][ident] = { 'ident' : ident,
                                              'type' : items[link][ident] }

# sort proc_ins to produce ordered output.txt
proc_ins = [ v for v in proc_ins.values() ]
proc_ins = sorted(proc_ins, key=lambda x: x['link'])

for page in proc_ins:
    idents = page['idents']
    idents = [ v for v in idents.values() ]
    idents = sorted(idents, key=lambda x: x['ident'])
    page['idents'] = idents

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

# returns the version number common to all declarations. Returns none if two
# declarations have different version numbers or if no version number is
# provided
def get_version(decls):
    rv = None
    for code,v in decls:
        if v:
            if rv == None:
                rv = v
            elif v != rv:
                return None
    return rv

def build_abstract(decls, desc):
    line_limit = MAX_CODE_LINES
    global debug_num_lines
    num_lines = 0

    limited = False
    all_code = ''

    for i,(code,ver) in enumerate(decls):
        code = code.strip()
        code = '<pre><code>' + code + '</code></pre>'
        code_num_lines = code.count('\n') + 1

        # limit the number of code snippets to be included so that total number
        # of lines is less than MAX_CODE_LINES. The limit becomes active only
        # for the second and subsequent snippets.
        first = True if i == 0 else False;
        last = True if i == len(decls)-1 else False;

        if not first:
            if last:
                if code_num_lines > line_limit:
                    limited = True
                    break
            else:
                if code_num_lines > line_limit - 1:
                    # -1 because we need to take into account
                    # <more overloads omitted> message
                    limited = True
                    break

        all_code += code
        num_lines += 1
        line_limit -= code_num_lines

    if limited:
        all_code += '<pre><code> &lt; omitted declarations &gt; </code></pre>'


    # count the number of lines used
    num_lines += all_code.count('\n')
    if len(desc) > 110:
        num_lines += 2
    else:
        num_lines += 1
    if limited:
        num_lines += 1

    debug_num_lines[num_lines] += 1

    if debug and num_lines >= 10:
        print("# error : large number of lines: ")
        print("# BEGIN ======")
        print(all_code + desc)
        print("# END ========")

    return all_code + desc

if debug:
    out = sys.stdout
else:
    out = open(output_file, 'w')

#i=1
for page in proc_ins:
    idents = page['idents']
    link = page['link']
    fn = page['fn']

    if debug_ident:
        ignore = True
        for ident in idents:
            if ident['ident'].find(debug_ident) != -1:
                ignore = False
                break
        if ignore:
            continue

    #print(str(i) + '/' + str(len(proc_ins)) + ': ' + link)
    #i+=1

    root = e.parse('reference/'+fn, parser=html.HTMLParser())

    for ident in idents:
        item_ident = ident['ident']
        item_type = ident['type']

        # get the name by extracting the unqualified identifier
        name = get_name(item_ident)

        try:
            debug_verbose = True if debug and debug_ident != None else False
            if item_type == ITEM_TYPE_CLASS:
                decls = get_declarations(root, name)
                desc = get_short_description(root, get_version(decls), debug=debug_verbose)
                abstract = build_abstract(decls, desc)

            elif item_type == ITEM_TYPE_FUNCTION:
                decls = get_declarations(root, name)
                desc = get_short_description(root, get_version(decls), debug=debug_verbose)
                abstract = build_abstract(decls, desc)

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
            line = item_ident + '\t'
            # type
            line += 'A\t'
            # redirect, otheruses, categories, references, see_also,
            # further_reading, external links, disambiguation, images
            line += '\t\t\t\t\t\t\t\t\t'
            # abstract
            abstract = abstract.replace('\n','\\n')
            line += abstract + '\t'
            # source url
            line += '[http://en.cppreference.com/w/' + link + ' Cppreference]\n'
            out.write(line)
        except DdgException as err:
            if debug:
                line = '# error (' + str(err) + "): " + link + ": " + item_ident + "\n"
                out.write(line)

if debug:
    print('=============================')
    print('Numbers of lines used:')
    for i,l in enumerate(debug_num_lines):
        print(str(i) + ': ' + str(l) + ' result(s)')
