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

from lxml import etree

from index_transform.devhelp_qch import convert_devhelp_to_qch


class TestConvertDevhelpToQch(unittest.TestCase):
    def test_convert_devhelp_to_qch(self):
        dir_path = os.path.dirname(__file__)
        index_fn = os.path.join(dir_path, 'devhelp_qch_data/devhelp-index.xml')
        file_list_fn = os.path.join(dir_path, 'devhelp_qch_data/file-list.xml')
        expected_path = os.path.join(dir_path, 'devhelp_qch_data/expected.xml')
        dest_path = os.path.join(dir_path, 'devhelp_qch_data/result.xml')

        parser = etree.XMLParser(encoding='UTF-8', recover=True)
        in_tree = etree.parse(index_fn, parser)
        in_root = in_tree.getroot()

        file_tree = etree.parse(file_list_fn, parser)
        files_root = file_tree.getroot()

        with open(expected_path, 'rb') as expected_f:
            expected = expected_f.read()

        result = convert_devhelp_to_qch(in_root, files_root, 'virtual_folder')

        if expected != result:
            with open(dest_path, 'wb') as result_f:
                result_f.write(result)

        self.assertEqual(expected, result)
