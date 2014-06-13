# -*- coding: utf-8 -*-

import unittest
import switchboard

class TestSwitchboard(unittest.TestCase):

    def test__take(self):
        d1 = {}
        self.assertEqual(None, switchboard._take(d1, 'key'))
        self.assertEqual('something', switchboard._take(d1, 'key', 'something'))
        self.assertEqual({}, d1)

        d2 = {'key': 'value'}
        self.assertEqual('value', switchboard._take(d2, 'key'))
        self.assertEqual(None, switchboard._take(d2, 'key'))
        self.assertEqual({}, d2)

    def test__get_cmds_id(self):
        self.assertEqual(None, switchboard._get_cmds_id([]))
        self.assertEqual(None, switchboard._get_cmds_id([[None, None], [None, None]]))

        self.assertEqual((0,), switchboard._get_cmds_id([None, None, 0]))
