#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from commands.preprocess import *
import unittest

class TestConvertLoaderName(unittest.TestCase):
    def test_convert_loader_name(self):
        url = 'http://en.cppreference.com/mwiki/load.php?debug=false&lang=en&\
modules=site&only=scripts&skin=cppreference2&*'
        self.assertEqual('site_scripts.js', convert_loader_name(url))

        url = 'http://en.cppreference.com/mwiki/load.php?debug=false&lang=en&\
modules=site&only=styles&skin=cppreference2&*'
        self.assertEqual('site_modules.css', convert_loader_name(url))

        url = 'http://en.cppreference.com/mwiki/load.php?debug=false&lang=en&\
modules=skins.cppreference2&only=scripts&skin=cppreference2&*'
        self.assertEqual('skin_scripts.js', convert_loader_name(url))

        url = 'http://en.cppreference.com/mwiki/load.php?debug=false&lang=en&\
modules=startup&only=scripts&skin=cppreference2&*'
        self.assertEqual('startup_scripts.js', convert_loader_name(url))

        url = 'http://en.cppreference.com/mwiki/load.php?debug=false&lang=en&\
modules=ext.gadget.ColiruCompiler%2CMathJax%7Cext.rtlcite%7Cmediawiki.\
legacy.commonPrint%2Cshared%7Cskins.cppreference2&only=styles&skin=\
cppreference2&*'
        self.assertEqual('ext.css', convert_loader_name(url))

        with self.assertRaises(Exception):
            convert_loader_name('')
