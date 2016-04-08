#!/usr/bin/python
"""
Tests the Wireframe
"""

import os
import sys
import os.path
from .. import pages

from selenium import webdriver
from django.test import LiveServerTestCase
from django.conf import settings

USERNAME = getattr(settings, 'SAUCE_USERNAME', False)
ACCESS_KEY = getattr(settings, 'SAUCE_ACCESS_KEY', False)

from sauceclient import SauceClient
sauce_client = SauceClient(USERNAME, ACCESS_KEY)

class AdvNavigationTest(LiveServerTestCase):

    baseurl = 'http://localhost:8001'

    def setUp(self):

        self.desired_cap = {
            'platform': "Mac OS X 10.9",
            'browserName': "chrome",
            'version': "31",
            'tags': ["wireframe"]
        }

        self.driver = webdriver.Remote(
            command_executor='http://%s:%s@ondemand.saucelabs.com:80/wd/hub' % (USERNAME, ACCESS_KEY),
            desired_capabilities=self.desired_cap)

        self.driver.implicitly_wait(20)

    def click_id(self, elid):
        self.driver.find_element_by_id(elid).click()

    def go_url(self, urlsuffix = ''):
        self.driver.get(self.baseurl + urlsuffix)

    def click_food(self):
        self.click_id('link_food')

    def click_discover(self):
        self.click_id('link_discover')

    def click_home(self):
        self.click_id('link_home')

    def click_filter(self):
        self.click_id('link_filter')

    def updateSauceName(self, name):
        sauce_client.jobs.update_job(self.driver.session_id, name=name)

    def tearDown(self):
        try:
            if sys.exc_info() == (None, None, None):
                sauce_client.jobs.update_job(self.driver.session_id, passed=True)
            else:
                sauce_client.jobs.update_job(self.driver.session_id, passed=False)
        finally:
            self.driver.quit()

    def test_breakfast(self):
        """SCOUT-8, testing to see if user can bring up list of b-fast
        places by clicking view more results"""

        self.updateSauceName("Wireframe: Home to Filter Breakfast")
        self.go_url()
        page = pages.HomePage(self.driver)
        page.click_results('breakfast')
        self.assertEqual('page_food', page.pageId)
        self.assertEqual(page.filterBy.text, "Open Period")
        self.assertEqual(page.placesCount.text, "4")

    def test_details(self):
        """testing to see if user can click on a place and then see more
        details from the home page"""

        self.updateSauceName("Wireframe: Home to Details")
        self.go_url()
        page = pages.HomePage(self.driver)
        page.click_place('open', 2)
        self.assertIn('page', page.pageId)
        self.assertEqual(page.foodName.text, "Banh & Naan, Husky Den")
        self.assertEqual(page.foodType.text, "FOOD COURT")


    def test_details2(self):
        """testing to see if user can click on a place and then see more
        details from the "places" page"""

        self.updateSauceName("Wireframe: Places to Details")
        self.go_url('/food/')
        page = pages.PlacesPage(self.driver)
        page.click_place(3)
        self.assertIn('page', page.pageId)
        self.assertEqual(page.foodName.text, "Banh & Naan, Husky Den")
        self.assertEqual(page.foodType.text, "FOOD COURT")
