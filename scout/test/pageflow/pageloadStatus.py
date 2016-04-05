#!/usr/bin/python
"""
A simple functional headless UI test with pyvirtualdisplay and selenium
Links and URLS
"""

import sys
import unittest
import copy

from django.test import LiveServerTestCase
from django.test import Client
from django.conf import settings

class UrlStatusTest(LiveServerTestCase):

    def clientUrlStatus(self, urlsuffix=''):
        """Returns the status code of the given URL"""
        res = self.client.get(urlsuffix)
        return res.status_code

    def assertUrlStatus(self, urlsuffix='', code=200):
        """Checks to see if the status code of the given URL matches the
        given status code"""
        self.assertEqual(self.clientUrlStatus(urlsuffix), code)

    # @wd.parallel.multiply
    def test_home_exists(self):
        """Test that the home page results in a 200"""
        # Home Page
        self.assertUrlStatus('/', 200)

    # @wd.parallel.multiply
    def test_food_exists(self):
        """Test that the food page results in a 200"""
        self.assertUrlStatus('/food/', 200)

    # @wd.parallel.multiply
    def test_filter_exists(self):
        """Test that the filter page results in a 200"""
        self.assertUrlStatus('/filter/', 200)

    # @wd.parallel.multiply
    def test_bad_detailURL(self):
        """Ensure a nonexistant space results in a 404 status code"""
        self.assertUrlStatus('/detail/12345679', 404)

    # uncomment for debugging
    # @unittest.expectedFailure
    # @wd.parallel.multiply
    def test_bad_homeURL(self):
        """Test an invalid URL and see if it results in a 404"""
        # Bad URL
        self.assertUrlStatus('/LSFDLK/', 404)

    # uncomment for debugging
    # @unittest.expectedFailure
    # @wd.parallel.multiply
    def test_redirect_URLs(self):
        """Test URLs that are meant to redirect(301)"""
        self.assertUrlStatus('/food', 301)
        self.assertUrlStatus('/filter', 301)