from django.conf import settings
from django.utils import unittest
from scout.test.space_dao import SpaceDAOTest

USERNAME = getattr(settings, 'SAUCE_USERNAME', False)
ACCESS_KEY = getattr(settings, 'SAUCE_ACCESS_KEY', False)

if USERNAME and ACCESS_KEY:
    from scout.test.navigation import NavigationTest
    from scout.test.fidelity_ui import UITest
    from scout.test.wireframe_navigation import WireframeTest
