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
from lxml.etree import strip_elements
import logging
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
    strip_style_tags(root)
    convert_span_tables_to_tr_td(root)

    head = os.path.dirname(dst_path)
    os.makedirs(head, exist_ok=True)

    with open(dst_path, 'wb') as a_file:
        root.getroottree().write(a_file, pretty_print=True, method="html",
                                 encoding='utf-8')
    return output

def preprocess_html_merge_css(root, src_path):
    log = logging.Logger('ignore')
    output = io.StringIO()
    handler = logging.StreamHandler(stream=output)
    formatter = logging.Formatter('%(levelname)s, %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    # cssutils_logging_handler of Premailer.__init__ is insufficient to silence
    # warnings to stderr in non-verbose mode
    cssutils.log.setLog(log)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        premailer = Premailer(root, base_url=src_path,
                              disable_link_rewrites=True, remove_classes=True)
        root = premailer.transform().getroot()

    return output.getvalue()

def strip_style_tags(root):
    strip_elements(root, 'style')

def needs_td_wrapper(element):
    # element has table:row
    if len(element.getchildren()) == 0:
        return True
    for el in element.getchildren():
        str_attrib_value = el.get('style')
        if str_attrib_value is not None and \
                str_attrib_value.find('display:table-cell;') is not None:
            return False
    return True

def remove_display_property_if_needed(element):
    atrib = cssutils.parseStyle(element.get('style'))
    atrib.removeProperty('display')
    element.set('style', atrib.getCssText(separator=''))
    if len(element.get('style')) == 0:
        element.attrib.pop('style')

def has_css_property_value(el, prop_name, prop_value):
    atrib = cssutils.parseStyle(el.get('style'))
    value = atrib.getPropertyCSSValue(prop_name)
    if value is not None and value.cssText == prop_value:
        return True
    return False

def convert_display_property_to_html_tag(element, element_tag, display_value):
    str_attrib_value = element.get('style')
    if str_attrib_value is None:
        return False
    if has_css_property_value(element, 'display', display_value):
        element.tag = element_tag
        remove_display_property_if_needed(element)
        return True

def convert_span_table_to_tr_td(table_el):
    table_el.tag = 'table'
    remove_display_property_if_needed(table_el)

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

def convert_span_tables_to_tr_td(root_el):

    # note that the following xpath expressions match only the prefix of the
    # CSS property value
    table_els = root_el.xpath('//span[contains(@style, "display:table")]')
    # root_el.xpath('//div[contains(@style, "display:inline-table")]')

    for table_el in table_els:
        if has_css_property_value(table_el, 'display', 'table'):
            convert_span_table_to_tr_td(table_el)
        #wrap_element(table_el, 'div', 'display:inline')
        #convert_span_table_to_tr_td(table_el)

    return root_el
