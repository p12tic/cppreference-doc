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

import lxml.etree as e
import re
from copy import deepcopy

class DdgException(Exception):
    pass

''' Returns the element in which the content is stored.
'''
def get_content_el(root_el):
    try:
        return root_el.xpath('''/html/body/div[@id="cpp-content-base"]
                            /div[@id="content"]
                            /div[@id="bodyContent"]
                            /div[@class="mw-content-ltr"]''')[0]
    except:
        raise DdgException("Could not find content element")

VERSION_C89 = 0
VERSION_C99 = 1
VERSION_C11 = 2
VERSION_CXX98 = 100
VERSION_CXX03 = 101
VERSION_CXX11 = 102
VERSION_CXX14 = 103

''' Returns the declaration of the feature with name 'name'.
    If several declarations with the same name are present, the standard
    revision marker is parsed and only the declarations for the latest standard
    are left. If there are still several declarations left in the viable
    declaration list, the first is returned.

    Return value: a tuple of three elements:
        1) the code of the declaration
        2) the version as defined by the 'num' dcl template parameter, or None
           if no version was specified.
        3) True if several viable declarations were still present after the
           filtering, False otherwise

    If no declaration is found, an exception of type DdgException is raised
'''
def get_declaration(root_el, name):
    content_el = get_content_el(root_el)

    dcl_tables = content_el.xpath('table[@class="t-ddcl-list"]')
    if len(dcl_tables) == 0:
        raise DdgException("dcl table not found")

    dcl_table = dcl_tables[0]

    parsed_dcls = []
    for dcl in dcl_table.xpath('tr[@class="t-ddcl-list-item"]'):
        code_els = dcl.xpath('td[1]/div/span[contains(@class, "mw-geshi")]')
        if len(code_els) == 0:
            continue

        code = code_els[0].text_content()
        code = re.sub('\n+', '\n', code)

        if (code.find(name) == -1):
            continue

        std_rev_els = dcl.xpath('td[3]/span[contains(@class, "t-mark")]')
        if len(std_rev_els) == 0:
            std_rev = VERSION_CXX98
        else:
            std_rev_str = std_rev_els[0].text_content().lower()
            if (std_rev_str.find('c++03') != -1):
                std_rev = VERSION_CXX03
            if (std_rev_str.find('c++11') != -1):
                std_rev = VERSION_CXX11
            if (std_rev_str.find('c++14') != -1):
                std_rev = VERSION_CXX14
            else:
                std_rev = VERSION_CXX98

        version = None
        try:
            version_str = dcl.xpath('td[2]')[0].text_content()
            version_str = re.search('\(([^)]*)\)', version_str).group(1)
            version = long(version_str)
        except:
            pass

        parsed_dcls.append((code, std_rev, version))

    if len(parsed_dcls) == 0:
        raise DdgException("dcl table contains no declarations")

    # filter out older standards
    max_std_rev = max(parsed_dcls, key=lambda x:x[1])[1]
    parsed_dcls = [ d for d in parsed_dcls if d[1] == max_std_rev ]

    if len(parsed_dcls) > 0:
        code = parsed_dcls[0][0]
        version = parsed_dcls[0][2]
        multi = False
        if len(parsed_dcls) > 1:
            multi = True

        return (code, version, multi)
    else:
        raise DdgException("No declarations after parsing")

''' Processes description text. Drops all tags except <code> and <i>. Replaces
    <b> with <i>. Replaces span.mw-geshi with <code>. Returns the processed
    description as str. The description is limited to one sentence (delimited
    by a dot) and a maximum of 200 characters. If the sentence is longer than
    200 characters, '...' is appended.
'''
def process_description(el):
    char_limit = 100

    el = deepcopy(el)   # we'll modify the tree
    el.tag = 'root'
    for t in el.xpath('.//span[contains(@class, "mw-geshi")]'):
        t.tag = 'code'

    for t in el.xpath('.//*'):
        if t.tag in ['code', 'i', 'b']:
            for key in t.attrib:
                del t.attrib[key]
        else:
            t.drop_tag()
    desc = e.tostring(el, method='html', encoding=str, with_tail=False)
    desc = desc.replace('<root>','').replace('</root>','')

    # Handle 'i.e.' as a special case
    desc = desc.replace('i.e.', 'ᚃ')

    # limit the number of characters
    num_code = desc.count('<code>')
    num_i = desc.count('<i>')
    num_b = desc.count('<b>')
    limit = char_limit + num_code * 13 + num_i * 7 + num_b * 7
    desc = desc[:limit]

    # find the last dot, remove broken tags
    last_open = -1
    last_close = -1
    open_count = 0
    first_dot = -1

    for t in re.finditer('<(/?(?:code|i|b))>', desc):
        if t.group(1)[0] != '/':

            if open_count == 0:
                last_open = t.start()
                # find any dots in the top level text
                if last_close != -1:
                    pos = desc[last_close:last_open].rfind('.')
                    if pos != -1 and first_dot == -1:
                        first_dot = last_close + pos
            open_count += 1

        else:
            open_count -= 1
            if open_count == 0:
                last_close = t.start()

    if open_count > 0:
        desc = desc[:last_open]

    if last_close == -1:
        last_close = 0

    pos = desc[last_close:].rfind('.')
    if pos != -1 and first_dot == -1:
        first_dot = last_close + pos

    if first_dot == -1 or first_dot > len(desc):
        iepos = desc.rfind('ᚃ')
        if iepos != -1 and iepos > 2:
            # string is too long but we can cut it at 'i.e.'
            if desc[iepos-2:iepos+1] == ', ᚃ':
                desc = desc[:iepos-2] + '.'
            elif desc[iepos-2:iepos+1] == ' ,ᚃ':
                desc = desc[:iepos-2] + '.'
            elif desc[iepos-1:iepos+1] == ',ᚃ':
                desc = desc[:iepos-1] + '.'
            elif desc[iepos-1:iepos+1] == ' ᚃ':
                desc = desc[:iepos-1] + '.'
            else:
                desc = desc[:iepos]
        else:
            desc = desc + '...'
    else:
        desc = desc[:first_dot] + '.'
    desc = desc.replace('ᚃ', 'i.e.')
    return desc


''' Returns a short description of a feature. This is the first sentence after
    the declaration (dcl template). If a list follows immediately, then the
    description is picked from a list item identified by num

    Raises DdgException on error
'''
def get_short_description(root_el, num):

    content_el = get_content_el(root_el)

    dcl_tables = content_el.xpath('table[@class="t-ddcl-list"]')
    if len(dcl_tables) == 0:
        raise DdgException("No dcl table found")
        #todo debug

    dcl_table = dcl_tables[0]

    desc_el = dcl_table.getnext()

    if desc_el == None:
        raise DdgException("No elements after dcl table")

    if desc_el.tag == 'p':
        return process_description(desc_el)
    elif desc_el.tag == 'div' and desc_el.get('class') == 't-li1':
        for el in dcl_table.xpath('div[@class="t-li1"]'):
            try:
                index_el = el.xpath('span[@class="t-li"]')[0]
                index = e.tostring(index_el, method='text')

                m = re.match('^\s*(\d*)\)\s*$', index)
                if m and int(m.group(1)) == num:
                    index_el.getparent().remove(index_el)
                    return process_description(el)

                m = re.match('^\s*(\d*)-(\d*)\)\s*$', index)
                if m and int(m.group(1)) <= num and int(m.group(2)) >= num:
                    index_el.getparent().remove(index_el)
                    return process_description(el)
            except None:
                pass
    raise DdgException("No description found")
