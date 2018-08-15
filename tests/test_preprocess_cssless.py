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

import os
import unittest
from commands.preprocess_cssless import *

class TestPreprocessHtmlMergeCss(unittest.TestCase):
    def test_preprocess_html_merge_cssless(self):
        dir_path = os.path.dirname(__file__)
        src_path = os.path.join(dir_path, 'preprocess_cssless_data/multiset.html')
        dst_path = os.path.join(dir_path, 'preprocess_cssless_data/multiset_out.html')
        expected_path = os.path.join(dir_path, 'preprocess_cssless_data/multiset_expected.html')

        preprocess_html_merge_cssless(src_path, dst_path)

        with open(dst_path, 'r') as a_file:
            test = a_file.read()

        with open(expected_path, 'r') as a_file:
            expected = a_file.read()

        self.assertEqual(test, expected)
        os.remove(dst_path)

    def test_preprocess_html_merge_cssless2(self):
        dir_path = os.path.dirname(__file__)
        src_path = os.path.join(dir_path, 'preprocess_cssless_data/basic_string.html')
        dst_path = os.path.join(dir_path, 'preprocess_cssless_data/basic_string_out.html')
        expected_path = os.path.join(dir_path, 'preprocess_cssless_data/basic_string_expected.html')

        preprocess_html_merge_cssless(src_path, dst_path)

        with open(dst_path, 'r') as a_file:
            test = a_file.read()

        with open(expected_path, 'r') as a_file:
            expected = a_file.read()

        self.assertEqual(test, expected)
        os.remove(dst_path)

class HTMLTestBase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def assert_converts_html(self, input, expected_output, function):
        input = '<html><body>{0}</body></html>'.format(input)
        expected_output = '<html><body>{0}</body></html>'.format(expected_output)

        parser = etree.HTMLParser()
        root = etree.fromstring(input, parser)

        root = function(root)

        output = etree.tostring(root, encoding=str, method='xml')

        self.assertEqual(expected_output, output)


class TestConvertSpanTablesToTrTd(HTMLTestBase):

    def assert_processes_table(self, input, expected_output):

        def test_fun(root):
            convert_span_tables_to_tr_td(root)
            return root

        self.assert_converts_html(input, expected_output, test_fun)

    def test_normal_table(self):
        input = '''\
<div>
  <one_more_block>
    <span style="border:solid 1.5px red; display:table; padding:2px">
      <span style="display:table-row;">
        <span style="border:solid 1px green; display:table-cell; padding:1.5px">1</span>
        <span style="border:none; display:table-cell; padding:1.5px">2</span>
      </span>
    </span>
  </one_more_block>
</div>
'''

        expected = '''\
<div>
  <one_more_block>
    <table style="border: solid 1.5px red;padding: 2px">
      <tr>
        <td style="border: solid 1px green;padding: 1.5px">1</td>
        <td style="border: none;padding: 1.5px">2</td>
      </tr>
    </table>
  </one_more_block>
</div>
'''
        self.assert_processes_table(input, expected)


    def test_wraps_table_row_text(self):
        input = '''\
<div>
  <one_more_block>
    <span style="border:solid 1.5px red; display:table; padding:2px">
      <span style="display:table-row;">little text</span>
    </span>
  </one_more_block>
</div>
'''

        expected = '''\
<div>
  <one_more_block>
    <table style="border: solid 1.5px red;padding: 2px">
      <tr><td>little text</td></tr>
    </table>
  </one_more_block>
</div>
'''
        self.assert_processes_table(input, expected)

    def test_wraps_into_td_table_row_children(self):
        input = '''\
<div>
  <one_more_block>
    <span style="border:solid 1.5px red; display:table; padding:2px">
      <span style="display:table-row;">
        <span>blabla</span>
        <span>blabla2</span>
      </span>
    </span>
  </one_more_block>
</div>
'''

        expected = '''\
<div>
  <one_more_block>
    <table style="border: solid 1.5px red;padding: 2px">
      <tr><td>
        <span>blabla</span>
        <span>blabla2</span>
      </td></tr>
    </table>
  </one_more_block>
</div>
'''
        self.assert_processes_table(input, expected)

    def test_wraps_into_td_table_row_children_with_style(self):
        input = '''\
<div>
  <one_more_block>
    <span style="border:solid 1.5px red; display:table; padding:2px">
      <span style="display:table-row">
        <span style="color:#008000; font-size:0.8em">(C++11)</span>
      </span>
    </span>
  </one_more_block>
</div>
'''

        expected = '''\
<div>
  <one_more_block>
    <table style="border: solid 1.5px red;padding: 2px">
      <tr><td>
        <span style="color:#008000; font-size:0.8em">(C++11)</span>
      </td></tr>
    </table>
  </one_more_block>
</div>
'''
        self.assert_processes_table(input, expected)

    def test_wraps_into_td_table_row_children_with_tags(self):
        input = '''\
<div>
  <one_more_block>
    <span style="border:solid 1.5px red; display:table; padding:2px">
      <span style="display:table-row;">
        <span>
          <div>bla</div>
        </span>
        <span>blabla2</span>
      </span>
    </span>
  </one_more_block>
</div>
'''

        expected = '''\
<div>
  <one_more_block>
    <table style="border: solid 1.5px red;padding: 2px">
      <tr><td>
        <span>
          <div>bla</div>
        </span>
        <span>blabla2</span>
      </td></tr>
    </table>
  </one_more_block>
</div>
'''
        self.assert_processes_table(input, expected)

    def test_does_not_wrap_into_td_children_when_not_in_table_row(self):
        input = '''\
<div>
  <one_more_block>
    <span style="border:solid 1.5px red; display:table; padding:2px">
      <span>
        <span style="display:table-cell;">2</span>
      </span>
    </span>
  </one_more_block>
</div>
'''

        expected = '''\
<div>
  <one_more_block>
    <table style="border: solid 1.5px red;padding: 2px">
      <span>
        <span style="display:table-cell;">2</span>
      </span>
    </table>
  </one_more_block>
</div>
'''
        self.assert_processes_table(input, expected)

    def test_does_not_wrap_children_when_sibling_is_td(self):
        input = '''\
<div>
  <one_more_block>
    <span style="border:solid 1.5px red; display:table; padding:2px">
      <span style="display:table-row;">
        <span>1</span>
        <span style="display:table-cell;">2</span>
      </span>
    </span>
  </one_more_block>
</div>
'''

        expected = '''\
<div>
  <one_more_block>
    <table style="border: solid 1.5px red;padding: 2px">
      <tr>
        <span>1</span>
        <td>2</td>
      </tr>
    </table>
  </one_more_block>
</div>
'''
        self.assert_processes_table(input, expected)

    def test_does_not_convert_tr_when_parent_is_not_table(self):
        input = '''\
<div>
  <one_more_block>
    <span style="border:solid 1.5px red; display:table; padding:2px">
      <span style="display:table-row;">
        <span style="display:table-row;">
          blabla
        </span>
      </span>
    </span>
  </one_more_block>
</div>
'''

        expected = '''\
<div>
  <one_more_block>
    <table style="border: solid 1.5px red;padding: 2px">
      <tr>
        <span style="display:table-row;">
          blabla
        </span>
      </tr>
    </table>
  </one_more_block>
</div>
'''
        self.assert_processes_table(input, expected)

    def test_does_not_convert_td_when_parent_is_not_tr(self):
        input = '''\
<div>
  <one_more_block>
    <span style="border:solid 1.5px red; display:table; padding:2px">
      <span style="display:table-cell;">
        <span style="display:table-cell;">
          blabla
        </span>
      </span>
    </span>
  </one_more_block>
</div>
'''

        expected = '''\
<div>
  <one_more_block>
    <table style="border: solid 1.5px red;padding: 2px">
      <span style="display:table-cell;">
        <span style="display:table-cell;">
          blabla
        </span>
      </span>
    </table>
  </one_more_block>
</div>
'''
        self.assert_processes_table(input, expected)


class TestConvertInlineBlockElementsToTable(HTMLTestBase):

    def perform_test(self, input, expected_output):
        def test_fun(root):
            convert_inline_block_elements_to_table(root)
            return root

        self.assert_converts_html(input, expected_output, test_fun)

    def test_does_not_convert_single(self):
        input = '''\
<div>
  <div style="display:inline-block; padding:0"/>
</div>
'''
        self.perform_test(input, input)

    def test_converts_multiple(self):
        input = '''\
<div>
  <div style="display:inline-block;"/>
  <div style="display:inline-table;"/>
</div>
'''

        expected = '''\
<div>
  <table style="padding:0; margin:0; border:none;"><tr><td><div style="display:inline-block;"/>
  </td><td><div style="display:inline-table;"/>
</td></tr></table></div>
'''
        self.perform_test(input, expected)


class TestConvertZeroTdWidthToNonzero(HTMLTestBase):

    def test_css_property(self):
        def test_fun(root):
            convert_zero_td_width_to_nonzero(root)
            return root

        input = '''\
<tr>
  <td style="white-space:nowrap; width:0%; border-top:1px solid #CCC">
  </td>
</tr>
'''

        expected = '''\
<tr>
  <td style="white-space: nowrap;border-top: 1px solid #CCC" width="1px">
  </td>
</tr>
'''

        self.assert_converts_html(input, expected, test_fun)

    def test_attribute(self):
        def test_fun(root):
            convert_zero_td_width_to_nonzero(root)
            return root

        input = '''\
<tr>
  <td width="0%">
  </td>
</tr>
'''

        expected = '''\
<tr>
  <td width="1px">
  </td>
</tr>
'''

        self.assert_converts_html(input, expected, test_fun)
