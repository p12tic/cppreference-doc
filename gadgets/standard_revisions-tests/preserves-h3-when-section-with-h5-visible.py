# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class PreservesH3WhenSectionWithH5Visible(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://en.cppreference.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_preserves_h3_when_section_with_h5_visible(self):
        driver = self.driver
        driver.get(self.base_url + "/w/test-gadget-stdrev/preserves-h3-when-section-with-h5-visible")
        try: self.assertTrue(driver.find_element_by_id("Should_always_be_visible").is_displayed())
        except AssertionError as e: self.verificationErrors.append(str(e))
        try: self.assertTrue(driver.find_element_by_id("Should_always_be_visible2").is_displayed())
        except AssertionError as e: self.verificationErrors.append(str(e))
        try: self.assertTrue(driver.find_element_by_id("Should_not_be_visible_in_cxx98").is_displayed())
        except AssertionError as e: self.verificationErrors.append(str(e))
        Select(driver.find_element_by_css_selector("select")).select_by_visible_text("C++98/03")
        try: self.assertTrue(driver.find_element_by_id("Should_always_be_visible").is_displayed())
        except AssertionError as e: self.verificationErrors.append(str(e))
        try: self.assertTrue(driver.find_element_by_id("Should_always_be_visible2").is_displayed())
        except AssertionError as e: self.verificationErrors.append(str(e))
        try: self.assertFalse(driver.find_element_by_id("Should_not_be_visible_in_cxx98").is_displayed())
        except AssertionError as e: self.verificationErrors.append(str(e))
        Select(driver.find_element_by_css_selector("select")).select_by_visible_text("C++11")
        try: self.assertTrue(driver.find_element_by_id("Should_always_be_visible").is_displayed())
        except AssertionError as e: self.verificationErrors.append(str(e))
        try: self.assertTrue(driver.find_element_by_id("Should_always_be_visible2").is_displayed())
        except AssertionError as e: self.verificationErrors.append(str(e))
        try: self.assertTrue(driver.find_element_by_id("Should_not_be_visible_in_cxx98").is_displayed())
        except AssertionError as e: self.verificationErrors.append(str(e))
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
