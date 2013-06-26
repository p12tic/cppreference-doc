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
    char_limit = 200
    min_paren_size = 40

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

    # description must never contain newlines
    desc = desc.replace('\n',' ')

    # Handle 'i.e.' and 'that is' as a special case
    desc = desc.replace('i.e.', 'ᚃ')
    desc = desc.replace('that is,', 'ᚄ')

    # process the description:
    # remove text in parentheses (except when it's within a tags
    # get the position of the cut of the description

    open_count = 0
    open_paren_count = 0

    del_ranges = []

    # remove parentheses
    for t in re.finditer('(<code>|</code>|<i>|</i>|<b>|</b>|\(|\))', desc):
        mt = t.group(1)

        if mt == '(':
            if open_count == 0:
                open_paren_count += 1
                if open_paren_count == 1:
                    last_paren_open = t.start()

        elif mt == ')':
            if open_count == 0 and open_paren_count > 0:
                open_paren_count -= 1
                if open_paren_count == 0:
                    end = t.start()+1
                    text = desc[last_paren_open:end]
                    if (text.find('ᚃ') != -1 or
                        text.find('ᚄ') != -1 or
                        len(text) > min_paren_size):
                        del_ranges.append((last_paren_open, t.start()+1))

        else:
            if mt[1] != '/':
                open_count += 1
            else:
                open_count -= 1

    for r in reversed(del_ranges):
        begin,end = r
        desc = desc[:begin] + desc[end:]

    # limit the number of characters
    num_code = desc.count('<code>')
    num_i = desc.count('<i>')
    num_b = desc.count('<b>')
    limit = char_limit + num_code * 13 + num_i * 7 + num_b * 7
    desc = desc[:limit]

    # find the first dot, actual limit when ignoring the tags
    last_open = -1
    last_close = 0
    open_count = 0
    first_dot = -1

    curr_limit= char_limit

    for t in re.finditer('(<code>|</code>|<i>|</i>|<b>|</b>)', desc):
        mt = t.group(1)

        if t.start() > curr_limit + len(mt):
            break

        curr_limit += len(mt)

        if t.group(1)[1] != '/':
            if open_count == 0:
                last_open = t.start()
                # find any dots in the top level text
                pos = desc[last_close:last_open].find('.')
                if pos != -1 and first_dot == -1:
                    first_dot = last_close + pos

            open_count += 1

        else:
            open_count -= 1
            if open_count == 0:
                last_close = t.start()

    # find dot if there were no tags (last_close == 0) or in the range after
    # the last close tag
    if first_dot == -1:
        pos = desc[last_close:].find('.')
        if pos != -1:
            first_dot = last_close + pos

    # limit desc to the adjusted limit
    # additionally strip unclosed tags (last_open < curr_limit)
    if open_count == 0:
        desc = desc[:curr_limit]
    else:
        desc = desc[:last_open]

    # limit desc to the first sentence. If first sentence is longer than the
    # limit, then try to cut desc at "i.e." if present. Otherwise, cut desc
    # in the middle of the sentence, preferably at the end of a word
    if first_dot == -1 or first_dot > len(desc):

        #find the last match
        m = None
        for m in re.finditer('[ᚃᚄ]', desc):
            pass
        if m and m.start() > 2:
            pos = m.start()
            char = m.group(0)

            # string is too long but we can cut it at 'i.e.'
            if desc[pos-2:pos+1] == ', '+char:
                desc = desc[:pos-2] + '.'
            elif desc[pos-2:pos+1] == ' ,'+char:
                desc = desc[:pos-2] + '.'
            elif desc[pos-1:pos+1] == ','+char:
                desc = desc[:pos-1] + '.'
            elif desc[pos-1:pos+1] == ' '+char:
                desc = desc[:pos-1] + '.'
            else:
                desc = desc[:pos]
        else:
            # open_count != 0 means that we are not within a word already
            if open_count == 0:
                m = None
                for m in re.finditer('[\s.]+', desc):
                    pass
                if m:
                    desc = desc[:m.start()]

            desc = desc + '...'
    else:
        desc = desc[:first_dot] + '.'
    desc = desc.replace('ᚃ', 'i.e.')
    desc = desc.replace('ᚄ', 'that is,')
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
