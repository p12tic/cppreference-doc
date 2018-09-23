#   Copyright (C) 2018  Monika Kairaityte <monika@kibit.lt>
#
#   This file is part of cppreference-doc
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see http://www.gnu.org/licenses/.

from premailer import Premailer
import cssutils
from lxml import html
from lxml import etree
from io import StringIO
import logging
import re
import os
import warnings
import io

def preprocess_html_merge_cssless(src_path, dst_path):
    with open(src_path, 'r') as a_file:
        content = a_file.read()
        parser = etree.HTMLParser()
        stripped = content.strip()
        root = etree.fromstring(stripped, parser)

    output = preprocess_html_merge_css(root, src_path)
    remove_display_none(root)
    convert_span_tables_to_tr_td(root)
    convert_inline_block_elements_to_table(root)
    convert_zero_td_width_to_nonzero(root)
    convert_font_size_property_to_pt(root, 16)
    convert_table_border_top_to_tr_background(root)

    head = os.path.dirname(dst_path)
    os.makedirs(head, exist_ok=True)

    with open(dst_path, 'wb') as a_file:
        root.getroottree().write(a_file, pretty_print=True, method="html",
                                 encoding='utf-8')
    return output

def silence_cssutils_warnings():
    log = logging.Logger('ignore')
    output = io.StringIO()
    handler = logging.StreamHandler(stream=output)
    formatter = logging.Formatter('%(levelname)s, %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    cssutils.log.setLog(log)

    return output

def preprocess_html_merge_css(root, src_path):
    # cssutils_logging_handler of Premailer.__init__ is insufficient to silence
    # warnings to stderr in non-verbose mode
    output = silence_cssutils_warnings()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        premailer = Premailer(root, base_url=src_path,
                              disable_link_rewrites=True,
                              remove_classes=True,
                              drop_style_tags=True)
        root = premailer.transform().getroot()

    return output.getvalue()

def needs_td_wrapper(element):
    # element has table:row
    if len(element.getchildren()) == 0:
        return True
    for el in element.getchildren():
        if get_css_property_value(el, 'display') in ('table-row', 'table-cell'):
            return False
    return True

def remove_css_property(el, prop_name):
    if el.get('style') is None:
        return

    decls = re.split(r'\s*;\s*', el.get('style'))
    if decls[-1] == '':
        decls.pop()

    idx = next((i for i,v in enumerate(decls) if v.startswith(prop_name + ':')), None)
    if idx is not None:
        del decls[idx]
        if len(decls) == 0:
            el.attrib.pop('style')
        else:
            el.set('style', ';'.join(decls))

def get_css_property_value(el, prop_name):
    if el.get('style') is None:
        return None

    for decl in re.split(r'\s*;\s*', el.get('style')):
        if decl.startswith(prop_name + ':'):
            return decl[len(prop_name)+1:].strip()
    return None

def has_css_property_value(el, prop_name, prop_value):
    if el.get('style') is None:
        return False

    regex = r'(^|;)\s*{}:\s*{}(;|$)'.format(re.escape(prop_name), re.escape(prop_value))
    return re.search(regex, el.get('style')) is not None

def set_css_property_value(el, prop_name, prop_value):
    decl = '{}: {}'.format(prop_name, prop_value)
    style = el.get('style')
    if style is None or style == '':
        el.set('style', decl)
    else:
        decls = re.split(r'\s*;\s*', style)
        if decls[-1] == '':
            decls.pop()

        try:
            idx = next(i for i,v in enumerate(decls) if v.startswith(prop_name + ':'))
            decls[idx] = decl
        except StopIteration:
            decls.append(decl)
        el.set('style', ';'.join(decls))

def convert_display_property_to_html_tag(element, element_tag, display_value):
    str_attrib_value = element.get('style')
    if str_attrib_value is None:
        return False
    if has_css_property_value(element, 'display', display_value):
        element.tag = element_tag
        remove_css_property(element, 'display')
        return True

def convert_span_table_to_tr_td(table_el):
    table_el.tag = 'table'
    remove_css_property(table_el, 'display')

    for element in table_el.getchildren():
        tag_renamed = convert_display_property_to_html_tag(element, 'tr',
                                                           'table-row')
        if tag_renamed:
            if needs_td_wrapper(element):
                td = etree.Element('td')
                for el in element.getchildren():
                    element.remove(el)
                    td.append(el)
                element.append(td)
                td.text = element.text
                element.text = None
            else:
                for child in element:
                    convert_display_property_to_html_tag(child, 'td',
                                                         'table-cell')

def wrap_element(el, tag_name, style):
    new_el = etree.Element(tag_name)
    new_el.set('style', style)
    el.addprevious(new_el)
    new_el.insert(0, el)

def remove_display_none(root_el):
    for el in root_el.xpath('//*[contains(@style, "display")]'):
        if has_css_property_value(el, 'display', 'none'):
            el.getparent().remove(el)

def convert_span_tables_to_tr_td(root_el):

    # note that the following xpath expressions match only the prefix of the
    # CSS property value
    table_els = root_el.xpath('//span[contains(@style, "display:table")]')

    for table_el in table_els:
        if has_css_property_value(table_el, 'display', 'table'):
            convert_span_table_to_tr_td(table_el)
        #wrap_element(table_el, 'div', 'display:inline')
        #convert_span_table_to_tr_td(table_el)

    return root_el

def convert_inline_block_elements_to_table(root_el):
    for el in root_el.xpath('//*[contains(@style, "display")]'):
        if get_css_property_value(el, 'display') not in ('inline-block', 'inline-table'):
            continue

        elements_to_put_into_table = [el]
        el = el.getnext()

        # find subsequent inline block elements
        while el is not None:
            if get_css_property_value(el, 'display') in ('inline-block', 'inline-table'):
                elements_to_put_into_table.append(el)
            else:
                break
            el = el.getnext()

        # only makes sense to put two or more to table
        if len(elements_to_put_into_table) < 2:
            continue

        # create table and put elements into it
        table_el = etree.Element('table')
        table_el.set('style', 'padding:0; margin:0; border:none;')

        elements_to_put_into_table[0].addprevious(table_el)

        tr = etree.SubElement(table_el, 'tr')

        for el in elements_to_put_into_table:
            td = etree.SubElement(tr, 'td')
            el.getparent().remove(el)
            td.append(el)

def get_table_rows(table_el):
    for el in table_el.iterchildren(['th', 'tr']):
        yield el
    for el in table_el.iterchildren(['thead', 'tbody', 'tfoot']):
        for el2 in el.iterchildren(['th', 'tr']):
            yield el2

def get_max_number_of_columns(table_el):
    max_tds = 0
    for row_el in get_table_rows(table_el):
        max_tds = max(max_tds, len(list(row_el.iterchildren('td'))))
    return max_tds

def clear_tr_border_top(tr_el):
    for td_el in tr_el.iterchildren('td'):
        remove_css_property(td_el, 'border-top')

def has_tr_border_top(tr_el):
    for td_el in tr_el.iterchildren('td'):
        if get_css_property_value(td_el, 'border-top') is not None:
            return True
    return False

def has_table_border_top(table_el):
    for tr_el in get_table_rows(table_el):
        if has_tr_border_top(tr_el):
            return True
    return False

def convert_table_border_top_to_tr_background(root_el):
    for table_el in root_el.iter('table'):
        if not has_table_border_top(table_el):
            continue

        td_count = get_max_number_of_columns(table_el)
        for tr_el in get_table_rows(table_el):
            if has_tr_border_top(tr_el):
                # TODO: handle border properties
                clear_tr_border_top(tr_el)
                border_tr = etree.Element('tr')
                border_td = etree.SubElement(border_tr, 'td')
                border_td.set('colspan', str(td_count))
                border_td.set('style', 'height:1px; font-size:1px; '
                                       'background-color: #ccc;')
                tr_el.addprevious(border_tr)


def convert_zero_td_width_to_nonzero(root_el):
    for el in root_el.xpath('//*[contains(@style, "width")]'):
        if has_css_property_value(el, 'width', '0%'):
            el.attrib['width'] = "1px"
            remove_css_property(el, 'width')

    for el in root_el.xpath('//*[contains(@width, "0%")]'):
        el.attrib['width'] = "1px"

def apply_font_size(size, parent_size_pt):
    size = size.strip()

    if size[-2:] == 'em':
        value_number = float(size[:-2].strip())
        return value_number*parent_size_pt

    if size[-2:] in ['pt', 'px']:
        return float(size[:-2].strip())

    if size[-1] == '%':
        value_number = float(size[:-1].strip())/100
        return value_number*parent_size_pt

    return parent_size_pt

def convert_font_size_property_to_pt_recurse(el, parent_size_pt):
    size_value = get_css_property_value(el,"font-size")

    if size_value:
        el_size_pt = apply_font_size(size_value, parent_size_pt)
        set_css_property_value(el, "font-size", "{}pt".format(el_size_pt))
    else:
        el_size_pt = parent_size_pt

    for child in el.getchildren():
        convert_font_size_property_to_pt_recurse(child, el_size_pt)

def convert_font_size_property_to_pt(root_el, default_size):
     convert_font_size_property_to_pt_recurse(root_el, default_size)
