import sys
import os
import unittest
from ddt import ddt, data
from cmdlinker.client import entry


@ddt
class TestCmd(unittest.TestCase):
    def test_show_version(self):
        sys.argv = ["CmdLinker", "-V"]
        with self.assertRaises(SystemExit) as cm:
            entry()
        self.assertEqual(cm.exception.code, 0)

    def test_help(self):
        sys.argv = ["CmdLinker", "-h"]
        with self.assertRaises(SystemExit) as cm:
            entry()
        self.assertEqual(cm.exception.code, 0)

    def test_init_help(self):
        sys.argv = ["CmdLinker", "init", "-h"]
        with self.assertRaises(SystemExit) as cm:
            entry()
        self.assertEqual(cm.exception.code, 0)

    def test_init(self):
        sys.argv = ["CmdLinker", "init"]
        with self.assertRaises(SystemExit) as cm:
            entry()
        self.assertEqual(cm.exception.code, 0)
