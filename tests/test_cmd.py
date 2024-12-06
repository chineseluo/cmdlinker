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

    def test_plan_load_help(self):
        sys.argv = ["Tk", "plan_load", "-h"]
        with self.assertRaises(SystemExit) as cm:
            entry()
        self.assertEqual(cm.exception.code, 0)