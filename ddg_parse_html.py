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

DESC_CHAR_LIMIT = 200
MAX_PAREN_SIZE = 40

''' Returns the declaration of the feature with name 'name'.
    If several declarations with the same name are present, and entries
    superseded in the later standards (as determined by the presence of until
    XXX marker) are ignored. The rest of declarations are returned as a list of
    tuples, each of which the two elements:
        1) the code of the declaration
        2) the version as defined by the 'num' dcl template parameter, or None
           if no version was specified.

    If no declaration is found, an exception of type DdgException is raised
'''
def get_declarations(root_el, name):
    content_el = get_content_el(root_el)

    dcl_tables = content_el.xpath('table[contains(@class, "t-dcl-begin")]')
    if len(dcl_tables) == 0:
        raise DdgException("dcl table not found")

    dcl_table = dcl_tables[0]

    dcls = []
    ignored = False
    for dcl in dcl_table.xpath('tbody/tr[contains(@class, "t-dcl")]'):
        code_els = dcl.xpath('td[1]/div/span[contains(@class, "mw-geshi")]')
        if len(code_els) == 0:
            ignored = True
            continue

        code = code_els[0].text_content()
        code = re.sub('\n+', '\n', code)

        # skip entries that don't contain name
        if re.search('[^a-zA-Z0-9_]' + re.escape(name) + '[^a-zA-Z0-9_]',
                     code) == None:
            ignored = True
            continue

        # skip deleted functions
        if re.search('=\s*delete\s*;', code) != None:
            ignored = True
            continue

        # ignore superseded entries
        std_rev_els = dcl.xpath('td[3]/span[contains(@class, "t-mark")]')
        if len(std_rev_els) != 0:
            txt = std_rev_els[0].text_content().lower()
            if txt.find('until') != -1:
                ignored = True
                continue

        version = None
        try:
            version_str = dcl.xpath('td[2]')[0].text_content()
            version_str = re.search('\((\d*)\)', version_str).group(1)
            version = int(version_str)
        except:
            pass

        dcls.append((code, version))

    if len(dcls) == 0:
        if not ignored:
            raise DdgException("dcl table contains no declarations")
        else:
            raise DdgException("All entries in dcl table were ignored")

    return dcls

def del_all_attrs(el):
    for key in el.attrib:
        del el.attrib[key]
''' Processes description text. Drops all tags except <code> and <i>. Replaces
    <b> with <i>. Replaces span.mw-geshi with <code>. Returns the processed
    description as str. The description is limited to one sentence (delimited
    by a dot) and a maximum of 200 characters. If the sentence is longer than
    200 characters, '...' is appended.
'''
def process_description(el, debug=False):

    el = deepcopy(el)   # we'll modify the tree
    el.tag = 'root'
    del_all_attrs(el)

    for t in el.xpath('.//span[contains(@class, "mw-geshi")]'):
        t.tag = 'code'

    for t in el.xpath('.//*'):
        if t.tag in ['code', 'i', 'b']:
            del_all_attrs(t)
        else:
            t.drop_tag()
    desc = e.tostring(el, method='html', encoding=str, with_tail=False)
    desc = desc.replace('<root>','').replace('</root>','')
    if debug:
        print("ROOT: " + desc)

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
                        len(text) > MAX_PAREN_SIZE):
                        del_ranges.append((last_paren_open, t.start()+1))

        else:
            if mt[1] != '/':
                open_count += 1
            else:
                open_count -= 1

    for r in reversed(del_ranges):
        begin,end = r
        desc = desc[:begin] + desc[end:]

    if debug:
        print("PAREN: " + desc)

    # find the first dot, actual limit when ignoring the tags
    last_open = -1
    last_close = 0
    open_count = 0
    first_dot = -1

    curr_limit= DESC_CHAR_LIMIT

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
    if debug:
        print("open_count: " + str(open_count))
        print("last_open: " + str(last_open))
        print("first_dot: " + str(first_dot))
        print("len: " + str(len(desc)))

    limited = False
    if len(desc) > curr_limit:
        limited = True
        if open_count == 0:
            desc = desc[:curr_limit]
        else:
            desc = desc[:last_open]

    if debug:
        print("limited: " + str(limited))
        print("open_count: " + str(open_count))
        print("last_open: " + str(last_open))
        print("first_dot: " + str(first_dot))
        print("LIMIT: " + desc)

    # limit desc to the first sentence. If first sentence is longer than the
    # limit, then try to cut desc at "i.e." if present. Otherwise, cut desc
    # in the middle of the sentence, preferably at the end of a word
    if limited and (first_dot == -1 or first_dot > len(desc)):
        # interrupted in the middle of a sentence. Polish the result

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
                for m in re.finditer('[\s]+', desc):
                    pass
                if m:
                    desc = desc[:m.start()]

            desc = desc + '...'
    else:
        desc = desc.rstrip()
        if first_dot == -1:
            # fix the punctuation at the end
            if desc[-1] in [';', ',']:
                desc = desc[:-1] + '.'
            if desc[-1] in [':', '-']:
                desc = desc + ' ...'
            elif desc[-1] != '.':
                desc = desc + '.'
        else:
            # cut the summary at the end of the first sentence
            desc = desc[:first_dot] + '.'

    desc = desc.replace('ᚃ', 'i.e.')
    desc = desc.replace('ᚄ', 'that is,')

    if debug:
        print("FINAL: " + desc)
    return desc

''' Returns a short description of a feature. This is the first sentence after
    the declaration (dcl template). If a list follows immediately, then the
    description is picked from a list item identified by num

    Raises DdgException on error
'''
def get_short_description(root_el, num, debug=False):

    content_el = get_content_el(root_el)

    dcl_tables = content_el.xpath('table[@class="t-dcl-begin"]')
    if len(dcl_tables) == 0:
        raise DdgException("No dcl table found")
        #todo debug

    dcl_table = dcl_tables[0]

    desc_el = dcl_table.getnext()

    if desc_el == None:
        raise DdgException("No elements after dcl table")

    if desc_el.tag == 'p':
        return process_description(desc_el, debug=debug)
    elif desc_el.tag == 'div' and desc_el.get('class') == 't-li1':
        if num == None:
            raise DdgException("Versioned summary with no version supplied")

        while (desc_el != None and desc_el.tag == 'div' and
            desc_el.get('class') == 't-li1'):
            index_els = desc_el.xpath('span[@class="t-li"]')
            if len(index_els) == 0:
                desc_el = desc_el.getnext()
                continue
            index_el = index_els[0]
            index = e.tostring(index_el, encoding=str,
                               method='text', with_tail=False)

            m = re.match('^\s*(\d+)\)\s*$', index)
            if m and int(m.group(1)) == num:
                index_el.drop_tree()
                return process_description(desc_el, debug=debug)

            m = re.match('^\s*(\d+)-(\d+)\)\s*$', index)
            if m and int(m.group(1)) <= num and int(m.group(2)) >= num:
                index_el.drop_tree()
                return process_description(desc_el, debug=debug)

            m = re.match('^\s*(\d+),(\d+)\)\s*$', index)
            if m and num in [int(m.group(1)), int(m.group(2))]:
                index_el.drop_tree()
                return process_description(desc_el, debug=debug)

            desc_el = desc_el.getnext()
        raise DdgException("List items are not numbered")

    raise DdgException("No description found")
