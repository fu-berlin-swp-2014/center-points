import unittest
from tempfile import NamedTemporaryFile

from centerpoints.cli import parse_arguments


class TestArgumentParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ptsf = NamedTemporaryFile()

    @classmethod
    def tearDownClass(cls):
        cls.ptsf.truncate()
        cls.ptsf.close()

    def test_algorithm_choice(self):
        self.assertRaises(SystemExit, parse_arguments, ["-1", "-2"])
        self.assertRaises(SystemExit, parse_arguments, ["-1", "-3"])
        self.assertRaises(SystemExit, parse_arguments, ["-2", "-3"])

    def test_format_choice(self):
        args = ["-1", "--json", "--csv", "", self.ptsf.name]
        self.assertRaises(SystemExit, parse_arguments, args)

        options = parse_arguments(["-1", "--json", self.ptsf.name])
        self.assertEqual("json", options.format)

        options = parse_arguments(["-1", self.ptsf.name])
        self.assertEqual("csv", options.format)

        options = parse_arguments(["-1", "--csv", ",", self.ptsf.name])
        self.assertEqual("csv", options.format)
        self.assertEqual(options.separator, ",", )

        options = parse_arguments(["-1", self.ptsf.name])
        self.assertEqual(options.format, "csv", )
        self.assertEqual(options.separator, "\t")
