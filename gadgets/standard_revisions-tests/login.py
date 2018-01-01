# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class LoginHtml(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://en.cppreference.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_login_html(self):
        driver = self.driver
        driver.get(self.base_url + "/mwiki/index.php?title=Special:UserLogout&returnto=Main+Page")
        driver.find_element_by_link_text("Log in").click()
        driver.find_element_by_id("wpName1").clear()
        driver.find_element_by_id("wpName1").send_keys("test5")
        driver.find_element_by_id("wpPassword1").clear()
        driver.find_element_by_id("wpPassword1").send_keys("test4")
        driver.find_element_by_id("wpLoginAttempt").click()
        self.assertEqual("Test5", driver.find_element_by_link_text("Test5").text)
    
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
