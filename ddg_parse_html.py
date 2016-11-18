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

def iterate_top_text(text, on_text=None):
    last_close = 0
    open_count = 0

    for match in re.finditer('(<code>|</code>|<i>|</i>|<b>|</b>)', text):
        if match.group(1)[1] != '/':
            if open_count == 0:
                on_text(last_close, text[last_close:match.start()])
            open_count += 1

        else:
            open_count -= 1
            if open_count == 0:
                last_close = match.start() + len(match.group(1))

    if open_count == 0:
        on_text(last_close, text[last_close:])

def remove_parentheses(desc, max_paren_text_size):

    open_paren_count = 0
    last_paren_open = 0

    del_ranges = []

    def on_text(pos, text):
        nonlocal open_paren_count, last_paren_open, del_ranges
        for match in re.finditer('(\(|\))', text):
            gr = match.group(1)
            if gr == '(':
                if open_paren_count == 0:
                    last_paren_open = pos + match.start()
                open_paren_count += 1
            else:
                open_paren_count -= 1
                if open_paren_count == 0:
                    end = pos + match.start()+1

                    if end - last_paren_open > max_paren_text_size:
                        del_ranges.append((last_paren_open, end))

                    if last_paren_open >= pos:
                        if text.find('ᚃ') != -1 or text.find('ᚄ') != -1:
                            del_ranges.append((last_paren_open, end))

    for r in reversed(del_ranges):
        begin,end = r
        desc = desc[:begin] + desc[end:]
    return desc

def split_sentences(desc):

    sentences = []

    sentence_start_pos = 0

    def on_text(pos, text):
        nonlocal sentence_start_pos
        dot_pos = text.find('.')
        if dot_pos != -1:
            dot_pos += pos
            sentences.append(desc[sentence_start_pos:dot_pos+1])
            sentence_start_pos = dot_pos+1

    iterate_top_text(desc, on_text)

    if len(desc[sentence_start_pos:].strip()) > 0:
        sentences.append(desc[sentence_start_pos:])

    return sentences

def remove_punctuation_at_end(sentence):
    return sentence.rstrip(' .,:;')

def trim_single_sentence_at_word(sentence, max_chars):

    last_valid_chunk = None
    last_valid_chunk_pos = 0

    def on_text(pos, text):
        nonlocal last_valid_chunk, last_valid_chunk_pos
        if pos <= max_chars:
            last_valid_chunk = text
            last_valid_chunk_pos = pos

    iterate_top_text(sentence, on_text)

    # split only single top-level chunk
    words = last_valid_chunk.split(' ')
    last_word = 0
    curr_pos = last_valid_chunk_pos
    for i, word in enumerate(words):
        curr_pos += len(word) + 1
        if curr_pos > max_chars:
            break
        last_word = i

    last_valid_chunk = ' '.join(words[:last_word+1])

    return sentence[:last_valid_chunk_pos] + last_valid_chunk

def trim_single_sentence(text, max_chars):
    if len(text) <= max_chars:
        return text

    # If the sentence is longer than the limit, then try to cut desc at "i.e."
    # if present. Otherwise, cut desc in the middle of the sentence, preferably
    # at the end of a word

    #find the first match
    ie_pos = None

    def on_ie_text(pos, match_text):
        nonlocal ie_pos
        m = next(re.finditer('[ᚃᚄ]', match_text), None)
        if m is not None and ie_pos is None:
            ie_pos = pos + m.start()

    iterate_top_text(text, on_ie_text)

    if ie_pos is not None:
        if ie_pos <= 2:
            return ''

        if ie_pos > max_chars:
            text = trim_single_sentence_at_word(text, max_chars)
        else:
            text = text[:ie_pos]

        return remove_punctuation_at_end(text) + '...'

    text = trim_single_sentence_at_word(text, max_chars)
    return remove_punctuation_at_end(text) + '...'

''' Processes description text. Drops all tags except <code> and <i>. Replaces
    <b> with <i>. Replaces span.mw-geshi with <code>. Returns the processed
    description as str.

    The description is limited to max_sentences number of sentences and
    max_chars number of characters (each delimited by a dot).
    If a single sentence is longer than max_chars characters, '...' is appended.

    Setting max_paren_text_size to controls the maximum number of characters in
    parenthesized text. If the size of parenthesized block exceeds that, it is
    removed. Such blocks within <code>, <b> or <i> tag are ignored.
'''
def process_description(el, max_sentences, max_chars,
                        max_paren_text_size, debug=False):

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
    # remove text in parentheses (except when it's within some tag)
    # get the position of the cut of the description

    open_count = 0
    open_paren_count = 0

    desc = remove_parentheses(desc, max_paren_text_size)
    sentences = split_sentences(desc)

    # limit sentence count
    if len(sentences) > max_sentences:
        sentences = sentences[:max_sentences]

    # coarse character limit
    char_count = 0
    last_sentence = len(sentences)
    for i, s in enumerate(sentences):
        char_count += len(s)
        if char_count > max_chars:
            last_sentence = i+1
            break
    sentences = sentences[:last_sentence]

    # trim the single sentence if needed
    if char_count > max_chars and len(sentences) == 1:
        sentences[0] = trim_single_sentence(sentences[0], max_chars)
    else:
        if sentences[-1].rstrip()[-1] != '.':
            sentences[-1] = remove_punctuation_at_end(sentences[-1]) + '...'

    desc = '\n'.join(sentences)
    desc = desc.replace('ᚃ', 'i.e.')
    desc = desc.replace('ᚄ', 'that is,')

    return desc

''' Returns a short description of a feature. This is the first sentence after
    the declaration (dcl template). If a list follows immediately, then the
    description is picked from a list item identified by num

    Raises DdgException on error
'''
def get_short_description(root_el, num, max_sentences=1, max_chars=200,
                          max_paren_text_size=40, debug=False):

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
        return process_description(desc_el, max_sentences, max_chars,
                                   max_paren_text_size, debug=debug)
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
                return process_description(desc_el, max_sentences, max_chars,
                                           max_paren_text_size, debug=debug)

            m = re.match('^\s*(\d+)-(\d+)\)\s*$', index)
            if m and int(m.group(1)) <= num and int(m.group(2)) >= num:
                index_el.drop_tree()
                return process_description(desc_el, max_sentences, max_chars,
                                           max_paren_text_size, debug=debug)

            m = re.match('^\s*(\d+),(\d+)\)\s*$', index)
            if m and num in [int(m.group(1)), int(m.group(2))]:
                index_el.drop_tree()
                return process_description(desc_el, max_sentences, max_chars,
                                           max_paren_text_size, debug=debug)

            desc_el = desc_el.getnext()
        raise DdgException("List items are not numbered")

    raise DdgException("No description found")
