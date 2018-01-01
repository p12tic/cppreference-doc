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
from base import CppTestCase

class RevlistWorksInDscItem(CppTestCase):
    def test_revlist_works_in_dsc_item(self):
        driver = self.driver
        driver.get(self.base_url + "/w/test-gadget-stdrev/revlist-works-in-dsc-item")
        self.assertRegexpMatches(driver.find_element_by_xpath("//body").text, r"^[\s\S]*std::not_visible_in_cxx98[\s\S]*$")
        self.assertRegexpMatches(driver.find_element_by_xpath("//body").text, r"^[\s\S]*std::not_visible_in_cxx11[\s\S]*$")

        Select(driver.find_element_by_css_selector("select")).select_by_visible_text("C++98/03")
        self.assertNotRegexpMatches(driver.find_element_by_xpath("//body").text, r"^[\s\S]*std::not_visible_in_cxx98[\s\S]*$")
        self.assertRegexpMatches(driver.find_element_by_xpath("//body").text, r"^[\s\S]*std::not_visible_in_cxx11[\s\S]*$")

        Select(driver.find_element_by_css_selector("select")).select_by_visible_text("C++11")
        self.assertRegexpMatches(driver.find_element_by_xpath("//body").text, r"^[\s\S]*std::not_visible_in_cxx98[\s\S]*$")
        self.assertNotRegexpMatches(driver.find_element_by_xpath("//body").text, r"^[\s\S]*std::not_visible_in_cxx11[\s\S]*$")

