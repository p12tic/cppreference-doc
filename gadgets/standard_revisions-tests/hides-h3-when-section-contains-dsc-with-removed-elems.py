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

class HidesH3WhenSectionContainsDscWithRemovedElems(CppTestCase):
    
    def test_hides_h3_when_section_contains_dsc_with_removed_elems(self):
        driver = self.driver
        self.get_page("test-gadget-stdrev/hides-h3-when-section-contains-dsc-with-removed-elems")
        self.assertTrue(driver.find_element_by_id("Should_be_removed_when_c.2B.2B98").is_displayed())

        self.select_cxx98()
        self.assertFalse(driver.find_element_by_id("Should_be_removed_when_c.2B.2B98").is_displayed())

        self.select_cxx11()
        self.assertTrue(driver.find_element_by_id("Should_be_removed_when_c.2B.2B98").is_displayed())

