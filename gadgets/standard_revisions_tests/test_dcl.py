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


class TestDcl(CppTestCase):
    def test_hides_dcl_items_in_dcl_rev(self):
        self.get_page("test-gadget-stdrev/hides-dcl-items-in-dcl-rev")
        self.assert_text_in_body("void always_visible")
        self.assert_text_in_body("void not_visible_in_cxx98")
        self.assert_text_in_body("void not_visible_in_cxx11")

        self.select_cxx98()
        self.assert_text_in_body("void always_visible")
        self.assert_text_not_in_body("void not_visible_in_cxx98")
        self.assert_text_in_body("void not_visible_in_cxx11")

        self.select_cxx11()
        self.assert_text_in_body("void always_visible")
        self.assert_text_in_body("void not_visible_in_cxx98")
        self.assert_text_not_in_body("void not_visible_in_cxx11")

    def test_hides_dcl_items_in_member(self):
        self.get_page("test-gadget-stdrev/hides-dcl-items-in-member")
        self.assert_text_in_body("void always_visible")
        self.assert_text_in_body("void not_visible_in_cxx98")
        self.assert_text_in_body("void not_visible_in_cxx11")

        self.select_cxx98()
        self.assert_text_in_body("void always_visible")
        self.assert_text_not_in_body("void not_visible_in_cxx98")
        self.assert_text_in_body("void not_visible_in_cxx11")

        self.select_cxx11()
        self.assert_text_in_body("void always_visible")
        self.assert_text_in_body("void not_visible_in_cxx98")
        self.assert_text_not_in_body("void not_visible_in_cxx11")

    def test_rewrites_numbers_in_dcl(self):
        self.get_page("test-gadget-stdrev/rewrites-numbers-in-dcl")
        self.assert_text_once_in_body('visible_since_cxx11_1')
        self.assert_text_once_in_body('visible_always_2')
        self.assert_text_once_in_body('visible_until_cxx14_3')
        self.assert_text_once_in_body('(1)')
        self.assert_text_once_in_body('(2)')
        self.assert_text_once_in_body('(3)')
        self.assert_text_once_in_body('1) option_1_visible_since_cxx11')
        self.assert_text_once_in_body('2) option_2_visible_always')
        self.assert_text_once_in_body('3) option_3_visible_until_cxx14')

        self.select_cxx98()
        self.assert_text_not_in_body('visible_since_cxx11_1')
        self.assert_text_once_in_body('visible_always_2')
        self.assert_text_once_in_body('visible_until_cxx14_3')
        self.assert_text_once_in_body('(1)')
        self.assert_text_once_in_body('(2)')
        self.assert_text_not_in_body('(3)')
        self.assert_text_not_in_body('option_1_visible_since_cxx11')
        self.assert_text_once_in_body('1) option_2_visible_always')
        self.assert_text_once_in_body('2) option_3_visible_until_cxx14')

        self.select_cxx11()
        self.assert_text_once_in_body('visible_since_cxx11_1')
        self.assert_text_once_in_body('visible_always_2')
        self.assert_text_once_in_body('visible_until_cxx14_3')
        self.assert_text_once_in_body('(1)')
        self.assert_text_once_in_body('(2)')
        self.assert_text_once_in_body('(3)')
        self.assert_text_once_in_body('1) option_1_visible_since_cxx11')
        self.assert_text_once_in_body('2) option_2_visible_always')
        self.assert_text_once_in_body('3) option_3_visible_until_cxx14')

        self.select_cxx14()
        self.assert_text_once_in_body('visible_since_cxx11_1')
        self.assert_text_once_in_body('visible_always_2')
        self.assert_text_not_in_body('visible_until_cxx14_3')
        self.assert_text_once_in_body('(1)')
        self.assert_text_once_in_body('(2)')
        self.assert_text_not_in_body('(3)')
        self.assert_text_once_in_body('1) option_1_visible_since_cxx11')
        self.assert_text_once_in_body('2) option_2_visible_always')
        self.assert_text_not_in_body('3) option_3_visible_until_cxx14')

    def test_rewrites_numbers_in_dcl_range(self):
        self.get_page("test-gadget-stdrev/rewrites-numbers-in-dcl-range")
        self.assert_text_once_in_body('visible_since_cxx11_1')
        self.assert_text_once_in_body('visible_on_cxx11_2')
        self.assert_text_once_in_body('visible_since_cxx14_2')
        self.assert_text_once_in_body('(1)')
        self.assert_text_once_in_body('(2)')

        self.select_cxx11()
        self.assert_text_once_in_body('visible_since_cxx11_1')
        self.assert_text_once_in_body('visible_on_cxx11_2')
        self.assert_text_once_in_body('(1)')
        self.assert_text_once_in_body('(2)')

        self.select_cxx14()
        self.assert_text_once_in_body('visible_since_cxx11_1')
        self.assert_text_once_in_body('visible_since_cxx14_2')
        self.assert_text_once_in_body('(1)')
        self.assert_text_once_in_body('(2)')
