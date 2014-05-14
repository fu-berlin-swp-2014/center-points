import pep8
import unittest
from glob import glob


class TestCodeFormat(unittest.TestCase):
    def test_pep8_conformance_core(self):
        files = glob('centerpoints/*.py')

        pep8style = pep8.StyleGuide()
        result = pep8style.check_files(files)
        self.assertEqual(result.total_errors, 0,
                "Sorry to nitpick :) Please fix you code style errors.")

    def test_pep8_conformance_tests(self):
        files = glob('test/*.py')

        pep8style = pep8.StyleGuide()
        result = pep8style.check_files(files)
        self.assertEqual( result.total_errors, 0,
                "Sorry to nitpick :) Please fix you code style errors.")
