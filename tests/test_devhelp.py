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

from index_transform.devhelp import transform_devhelp


class TestTransformDevhelp(unittest.TestCase):
    def test_transform_devhelp(self):
        dir_path = os.path.dirname(__file__)
        chapters_fn = os.path.join(
            dir_path, 'transform_data/index-chapters-cpp.xml')
        functions_fn = os.path.join(
            dir_path, 'transform_data/index-functions-cpp.xml')
        expected_path = os.path.join(
            dir_path, 'devhelp_data/expected.xml')
        dest_path = os.path.join(dir_path, 'devhelp_data/result.xml')

        with open(expected_path, 'rb') as expected_f:
            expected = expected_f.read()

        result = transform_devhelp('book_title', 'book_name', 'book_base',
                                   'rel_link', chapters_fn, functions_fn)

        if expected != result:
            with open(dest_path, 'wb') as result_f:
                result_f.write(result)

        self.assertEqual(expected, result)
