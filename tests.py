# -*- coding: UTF-8 -*-
# Copyright (c) 2018 Intermix Software, Inc.
#
# This module is part of the Intermix Python Plugin and is released under the MIT
# License: https://opensource.org/licenses/MIT

from __future__ import unicode_literals

import base64
import json
import unittest

import intermix

BASE_ANNOTATION = {'module': '__main__', 'file': 'tests.py', 'plugin': 'intermix-python-plugin', 'plugin_ver': '0.7',
                   'app_ver': 1, 'user': '', 'format': 'intermix', 'version': '1', 'meta': {}}


def decoder(annotation):
    """ Decode the annotated format, skipping the header """
    return json.loads(base64.b64decode(annotation[16:-24]))


class IntermixTest(unittest.TestCase):

    @classmethod
    def test_class_method(cls):
        expected = BASE_ANNOTATION.copy()
        expected.update({'function': 'test_class_method', 'task': 'class_method', 'dag': 'in_a_class',
                         'app': 'test_app', 'linenumber': '32', 'classname': 'IntermixTest'})
        annotated = decoder(intermix.annotate('select * from users;', 'test_app', 1, dag='in_a_class',
                                              task='class_method'))
        del annotated['at']
        helper.assertDictEqual(expected, annotated)

    @staticmethod
    def test_static_method():
        expected = BASE_ANNOTATION.copy()
        expected.update({'function': 'test_static_method', 'task': 'static_method', 'dag': 'in_a_class',
                         'app': 'test_app', 'linenumber': '42', 'classname': ''})
        annotated = decoder(intermix.annotate('select * from users;', 'test_app', 1, dag='in_a_class',
                                              task='static_method'))
        del annotated['at']
        helper.assertDictEqual(expected, annotated)

    def test_empty_SQL(self):
        expected = BASE_ANNOTATION.copy()
        expected.update({'function': 'test_empty_SQL', 'task': 'test_empty_SQL', 'dag': 'in_a_class',
                         'app': 'test_app', 'linenumber': '51', 'classname': 'IntermixTest'})
        annotated = decoder(intermix.annotate('/*               */;', 'test_app', 1, dag='in_a_class',
                                              task='test_empty_SQL'))
        del annotated['at']
        self.assertDictEqual(expected, annotated)

    def test_basic_SQL(self):
        expected = BASE_ANNOTATION.copy()
        expected.update({'function': 'test_basic_SQL', 'task': 'test_basic_SQL', 'dag': 'in_a_class',
                         'app': 'test_app', 'linenumber': '60', 'classname': 'IntermixTest'})
        annotated = decoder(intermix.annotate('select € from users;', 'test_app', 1, dag='in_a_class',
                                              task='test_basic_SQL'))
        del annotated['at']
        self.assertDictEqual(expected, annotated)

    def test_nested_function(self):
        def foo():
            return intermix.annotate('select * from users;', 'test_app', '2', dag='in_a_class', task='nested')

        expected = BASE_ANNOTATION.copy()
        expected.update({'function': 'foo', 'task': 'nested', 'dag': 'in_a_class',
                         'app': 'test_app', 'linenumber': '66', 'classname': '', 'app_ver': '2'})
        annotated = decoder(foo())
        del annotated['at']
        self.assertDictEqual(expected, annotated)

    def test_already_exists(self):
        sql = intermix.annotate('/* INTERMIX_ID: deadbeef */ select * from users;', 'test_app\u0203', 1, dag='test€',
                                task='nested', override=False)
        self.assertEqual('/* INTERMIX_ID: deadbeef */ select * from users;', sql)

    def test_already_exists_overridden(self):
        expected = BASE_ANNOTATION.copy()
        expected.update({'function': 'test_already_exists_overridden', 'task': 'overriden', 'dag': 'test€',
                         'app': 'test_app\u0203', 'linenumber': '85', 'classname': 'IntermixTest'})
        annotated = decoder(intermix.annotate('/* INTERMIX_ID: deadbeef */ select * from users;', 'test_app\u0203', 1,
                                              dag='test€', task='overriden'))
        del annotated['at']
        self.assertDictEqual(expected, annotated)


def test_bare_function():
    """ We want to test annotations in a function outside of a class """
    # Helper to access asserts
    expected = BASE_ANNOTATION.copy()
    expected.update({'function': 'test_bare_function', 'task': 'function', 'dag': 'bare', 'app': 'test_app',
                     'linenumber': '96', 'classname': ''})
    annotated = decoder(intermix.annotate('select * from users;', 'test_app', 1, dag='bare', task='function'))
    del annotated['at']
    helper.assertDictEqual(expected, annotated)


if __name__ == '__main__':
    # Test code running outside of function
    helper = unittest.FunctionTestCase(lambda: None)
    expected = BASE_ANNOTATION.copy()
    expected.update({'function': '<module>', 'task': 'outside_of_function', 'dag': 'bare', 'app': 'test_app',
                     'linenumber': '108', 'classname': ''})
    annotated = decoder(intermix.annotate('select * from users;', 'test_app', 1, dag='bare',
                                          task='outside_of_function'))
    del annotated['at']
    helper.assertDictEqual(expected, annotated)

    unittest.FunctionTestCase(test_bare_function).debug()

    unittest.main()
