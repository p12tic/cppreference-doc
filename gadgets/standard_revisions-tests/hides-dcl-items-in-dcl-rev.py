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

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
from base import *

class HidesDclItemsInDclRev(CppTestCase):
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
