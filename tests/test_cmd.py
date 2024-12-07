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

    def test_init_file(self):
        sys.argv = ["CmdLinker", "init", "-f", "E:\开源项目\CmdLinker\Ost.yaml"]
        with self.assertRaises(SystemExit) as cm:
            entry()
        self.assertEqual(cm.exception.code, 0)

    def test_init_file_out(self):
        sys.argv = ["CmdLinker", "init", "-f", "E:\开源项目\CmdLinker\Ost.yaml", "-o", "../"]
        with self.assertRaises(SystemExit) as cm:
            entry()
        self.assertEqual(cm.exception.code, 0)

    def test_init_file_out_module(self):
        sys.argv = ["CmdLinker", "init", "-f", "E:\开源项目\CmdLinker\Ost.yaml", "-o", "../", "-m", "Luo"]
        with self.assertRaises(SystemExit) as cm:
            entry()
        self.assertEqual(cm.exception.code, 0)
