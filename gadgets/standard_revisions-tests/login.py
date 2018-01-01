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

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
