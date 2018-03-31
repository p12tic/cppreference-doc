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
    def test_preprocess_html_merge_css(self):
        src_path = 'tests/preprocess_cssless_data/multiset.html'
        dst_path = 'tests/preprocess_cssless_data/multiset_out.html'
        expected_path = 'tests/preprocess_cssless_data/multiset_expected.html'

        preprocess_html_merge_css(src_path, dst_path)
        with open(dst_path, 'r') as a_file:
            test = a_file.read()

        with open(expected_path, 'r') as a_file:
            expected = a_file.read()

        self.assertEqual(test, expected)
        os.remove(dst_path)
