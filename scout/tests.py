from django.conf import settings
from django.utils import unittest
from scout.test.spacedao.space_dao import SpaceDAOTest


USERNAME = getattr(settings, 'SAUCE_USERNAME', False)
ACCESS_KEY = getattr(settings, 'SAUCE_ACCESS_KEY', False)

if USERNAME and ACCESS_KEY:
    from scout.test.navigation import NavigationTest
    from scout.test.ui.filter import FilterTest
    from scout.test.wireframe.wireframe_navigation import AdvNavigationTest
    from scout.test.pageflow.navigation import MainNavigationTest
    from scout.test.pageflow.pageloadStatus import UrlStatusTest
    from scout.test.pageflow.content import ContentTest
