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

import unittest

from selenium import webdriver
from selenium.webdriver.support.ui import Select


class Driver:
    def __init__(self):
        base_url = "http://en.cppreference.com/"
        driver = webdriver.Firefox()
        driver.implicitly_wait(30)
        try:
            driver.get(base_url + "/mwiki/index.php?title=Special:UserLogout&returnto=Main+Page")  # noqa
            driver.get(base_url + "/mwiki/index.php?title=Special:UserLogin&returnto=Main+Page")  # noqa
            driver.find_element_by_id("wpName1").clear()
            driver.find_element_by_id("wpName1").send_keys("test5")
            driver.find_element_by_id("wpPassword1").clear()
            driver.find_element_by_id("wpPassword1").send_keys("test4")
            driver.find_element_by_id("wpLoginAttempt").click()
            if driver.find_element_by_link_text("Test5").text != "Test5":
                raise Exception("Could not login")
        except Exception:
            driver.quit()
            raise
        self.driver = driver
        self.base_url = base_url

    def __del__(self):
        self.driver.quit()


driver_instance = Driver()


class CppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.base_url = driver_instance.base_url
        self.driver = driver_instance.driver

    def setUp(self):
        self.cached_body = None

    def get_page(self, title):
        self.driver.get(self.base_url + "/w/" + title)
        self.cached_body = None

    def select_standard(self, std):
        s = Select(self.driver.find_element_by_css_selector("select"))
        s.select_by_visible_text(std)
        self.cached_body = None

    def select_diff(self):
        self.select_standard("C++98/03")

    def select_cxx98(self):
        self.select_standard("C++98/03")

    def select_cxx11(self):
        self.select_standard("C++11")

    def select_cxx14(self):
        self.select_standard("C++14")

    def select_cxx17(self):
        self.select_standard("C++17")

    def select_cxx20(self):
        self.select_standard("C++20")

    def get_body_cached(self):
        if self.cached_body is None:
            self.cached_body = self.driver.find_element_by_xpath("//body").text
        return self.cached_body

    def assert_text_in_body(self, pattern):
        text = self.get_body_cached()
        self.assertIn(pattern, text)

    def assert_text_not_in_body(self, pattern):
        text = self.get_body_cached()
        self.assertNotIn(pattern, text)

    def text_occurrences_in_body(self, pattern):
        return self.driver.find_element_by_xpath("//body").text.count(pattern)

    def assert_text_occurrences_in_body(self, num, pattern):
        occurrences = self.text_occurrences_in_body(pattern)
        self.assertEqual(num, occurrences)

    def assert_text_once_in_body(self, pattern):
        self.assert_text_occurrences_in_body(1, pattern)
