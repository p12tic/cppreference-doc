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
# noqa

from base import CppTestCase


class TestSectionHierarchy(CppTestCase):

    def test_hides_h3_when_section_contains_dsc_with_removed_elems(self):
        driver = self.driver
        self.get_page("test-gadget-stdrev/hides-h3-when-section-contains-dsc-with-removed-elems")  # noqa
        self.assertTrue(driver.find_element_by_id("Should_be_removed_when_c.2B.2B98").is_displayed())  # noqa

        self.select_cxx98()
        self.assertFalse(driver.find_element_by_id("Should_be_removed_when_c.2B.2B98").is_displayed())  # noqa

        self.select_cxx11()
        self.assertTrue(driver.find_element_by_id("Should_be_removed_when_c.2B.2B98").is_displayed())  # noqa

    def test_hides_h3_when_section_contains_dsc_with_removed_until(self):
        driver = self.driver
        self.get_page("test-gadget-stdrev/hides-h3-when-section-contains-dsc-with-removed-until")  # noqa
        self.assertTrue(driver.find_element_by_id("Should_be_removed_when_c.2B.2B11").is_displayed())  # noqa

        self.select_cxx98()
        self.assertTrue(driver.find_element_by_id("Should_be_removed_when_c.2B.2B11").is_displayed())  # noqa

        self.select_cxx11()
        self.assertFalse(driver.find_element_by_id("Should_be_removed_when_c.2B.2B11").is_displayed())  # noqa

    def test_hides_h3_when_section_contains_only_stdrev(self):
        driver = self.driver
        self.get_page("test-gadget-stdrev/hides-h3-when-section-contains-only-stdrev")  # noqa
        self.assertTrue(driver.find_element_by_id("Should_be_removed_in_cxx98").is_displayed())  # noqa

        self.select_cxx98()
        self.assertFalse(driver.find_element_by_id("Should_be_removed_in_cxx98").is_displayed())  # noqa

        self.select_cxx11()
        self.assertTrue(driver.find_element_by_id("Should_be_removed_in_cxx98").is_displayed())  # noqa

    def test_preserves_h3_when_section_visible(self):
        driver = self.driver
        self.get_page("test-gadget-stdrev/preserves-h3-when-section-with-h5-visible")  # noqa
        self.assertTrue(driver.find_element_by_id("Should_always_be_visible").is_displayed())  # noqa

        self.select_cxx98()
        self.assertTrue(driver.find_element_by_id("Should_always_be_visible").is_displayed())  # noqa

        self.select_cxx11()
        self.assertTrue(driver.find_element_by_id("Should_always_be_visible").is_displayed())  # noqa

    def test_preserves_h3_when_section_with_h5_visible(self):
        driver = self.driver
        self.get_page("test-gadget-stdrev/preserves-h3-when-section-with-h5-visible")  # noqa
        self.assertTrue(driver.find_element_by_id("Should_always_be_visible").is_displayed())  # noqa
        self.assertTrue(driver.find_element_by_id("Should_always_be_visible2").is_displayed())  # noqa
        self.assertTrue(driver.find_element_by_id("Should_not_be_visible_in_cxx98").is_displayed())  # noqa

        self.select_cxx98()
        self.assertTrue(driver.find_element_by_id("Should_always_be_visible").is_displayed())  # noqa
        self.assertTrue(driver.find_element_by_id("Should_always_be_visible2").is_displayed())  # noqa
        self.assertFalse(driver.find_element_by_id("Should_not_be_visible_in_cxx98").is_displayed())  # noqa

        self.select_cxx11()
        self.assertTrue(driver.find_element_by_id("Should_always_be_visible").is_displayed())  # noqa
        self.assertTrue(driver.find_element_by_id("Should_always_be_visible2").is_displayed())  # noqa
        self.assertTrue(driver.find_element_by_id("Should_not_be_visible_in_cxx98").is_displayed())  # noqa
