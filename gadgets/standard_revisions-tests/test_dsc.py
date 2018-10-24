'''
    Copyright (C) 2017-2018  Povilas Kanapickas <povilas@radix.lt>

    This file is part of cppreference.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see http://www.gnu.org/licenses/.
'''

from base import CppTestCase


class TestDsc(CppTestCase):
    def test_hides_dsc_items_with_explicit_mark(self):
        self.get_page("test-gadget-stdrev/hides-dsc-items-with-explicit-mark")
        self.assert_text_in_body("std::not_visible_in_cxx98")
        self.assert_text_in_body("std::not_visible_in_cxx11")

        self.select_cxx98()
        self.assert_text_not_in_body("std::not_visible_in_cxx98")
        self.assert_text_in_body("std::not_visible_in_cxx11")

        self.select_cxx11()
        self.assert_text_in_body("std::not_visible_in_cxx98")
        self.assert_text_not_in_body("std::not_visible_in_cxx11")
