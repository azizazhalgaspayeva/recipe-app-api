"""
Sample tests
"""

from django.test import SimpleTestCase
from app import calc


class CalcTests(SimpleTestCase):
    """ Test the calc module. """

    def test_add(self):
        """ Test adding numbers together. """
        res = calc.add(100, 10)
        self.assertEqual(res, 110)
