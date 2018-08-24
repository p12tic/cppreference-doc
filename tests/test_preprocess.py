#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright (C) 2018  Monika Kairaityte <monika@kibit.lt>
#
#   This file is part of cppreference-doc
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see http://www.gnu.org/licenses/.

from commands.preprocess import *
import unittest
from lxml import etree

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

class TestHasClass(unittest.TestCase):
    def test_has_class(self):
        el = etree.Element('tag')
        self.assertEqual(False, has_class(el, []))
        self.assertEqual(False, has_class(el, ['']))
        self.assertEqual(False, has_class(el, ['a']))
        self.assertEqual(False, has_class(el, ['tag']))

        el.set('class', '')
        self.assertEqual(False, has_class(el, []))
        self.assertEqual(False, has_class(el, ['']))
        self.assertEqual(False, has_class(el, ['a']))
        self.assertEqual(False, has_class(el, ['tag']))

        el.set('class', 'a')
        self.assertEqual(False, has_class(el, []))
        self.assertEqual(False, has_class(el, ['']))
        self.assertEqual(True, has_class(el, ['a']))
        self.assertEqual(False, has_class(el, ['b']))
        self.assertEqual(False, has_class(el, ['tag']))
        self.assertEqual(True, has_class(el, ['a', 'b']))
        self.assertEqual(True, has_class(el, ['b', 'a']))
        self.assertEqual(False, has_class(el, ['b', 'c']))

        el.set('class', 'a b')
        self.assertEqual(False, has_class(el, []))
        self.assertEqual(False, has_class(el, ['']))
        self.assertEqual(True, has_class(el, ['a']))
        self.assertEqual(True, has_class(el, ['b']))
        self.assertEqual(False, has_class(el, ['tag']))
        self.assertEqual(True, has_class(el, ['a', 'b']))
        self.assertEqual(True, has_class(el, ['b', 'a']))
        self.assertEqual(True, has_class(el, ['b', 'c']))

        el.set('class', 'a  b')
        self.assertEqual(False, has_class(el, []))
        self.assertEqual(False, has_class(el, ['']))
        self.assertEqual(True, has_class(el, ['a']))
        self.assertEqual(True, has_class(el, ['b']))
        self.assertEqual(False, has_class(el, ['tag']))
        self.assertEqual(True, has_class(el, ['a', 'b']))
        self.assertEqual(True, has_class(el, ['b', 'a']))
        self.assertEqual(True, has_class(el, ['b', 'c']))

class TestIsExternalLink(unittest.TestCase):
    def test_is_external_link(self):
        self.assertEqual(True, is_external_link('http://a'))
        self.assertEqual(True, is_external_link('https://a'))
        self.assertEqual(True, is_external_link('ftp://a'))
        self.assertEqual(False, is_external_link('ahttp://a'))
        self.assertEqual(False, is_external_link(' http://a'))

class TestPlaceholderLinks(unittest.TestCase):
    # Placeholder link replacement is implemented in the MediaWiki site JS at
    # https://en.cppreference.com/w/MediaWiki:Common.js

    def test_is_ranges_placeholder(self):
        match = [
            'http://en.cppreference.com/w/cpp/ranges-placeholder/concepts/Assignable',
            'http://en.cppreference.com/w/cpp/ranges-placeholder/iterator/Incrementable',
            'http://en.cppreference.com/w/cpp/ranges-algorithm-placeholder/all_any_none_of',
            'http://en.cppreference.com/w/cpp/ranges-iterator-placeholder/dangling',
            'http://en.cppreference.com/w/cpp/ranges-utility-placeholder/swap',
        ]
        for target in match:
            self.assertTrue(is_ranges_placeholder(target),
                msg="Should match '{}'".format(target))

            target = target.replace("http://", "https://")
            self.assertTrue(is_ranges_placeholder(target),
                msg="Should match '{}'".format(target))

        nomatch = [
            'http://en.cppreference.com/w/cpp/ranges--placeholder/swap',
            'https://en.cppreference.com/w/cpp/ranges--placeholder/swap',
            'http://www.mediawiki.org/',
            'http://en.cppreference.com/w/Cppreference:About',
            'http://en.wikipedia.org/wiki/Normal_distribution',
            'https://www.mediawiki.org/',
            'https://en.cppreference.com/w/Cppreference:About',
            'https://en.wikipedia.org/wiki/Normal_distribution',
            'w/cpp.html',
            'w/cpp/language/expressions.html',
            '../utility/functional/is_placeholder.html',
            'utility/functional/placeholders.html',
            'w/cpp/experimental/ranges.html',
        ]
        for target in nomatch:
            self.assertFalse(is_ranges_placeholder(target),
                msg="Should not match '{}'".format(target))

    def test_transform_ranges_placeholder(self):
        entries = [
            # (target, file, expected)
            ('http://en.cppreference.com/w/cpp/ranges-placeholder/concepts/Assignable',
             'output/reference/en/cpp/concepts/ConvertibleTo.html',
             'Assignable.html'),

            ('http://en.cppreference.com/w/cpp/ranges-placeholder/concepts/Assignable',
             'output/reference/en/cpp/concepts/long/path/ConvertibleTo.html',
             '../../Assignable.html'),

            ('http://en.cppreference.com/w/cpp/ranges-placeholder/concepts/Assignable',
             'output/reference/en/cpp/other/path/ConvertibleTo.html',
             '../../concepts/Assignable.html'),

            ('http://en.cppreference.com/w/cpp/ranges-algorithm-placeholder/all_any_none_of',
             'output/reference/en/cpp/concepts/ConvertibleTo.html',
             '../algorithm/ranges/all_any_none_of.html'),

            ('http://en.cppreference.com/w/cpp/ranges-algorithm-placeholder/all_any_none_of',
             'output/reference/en/cpp/algorithm/ConvertibleTo.html',
             'ranges/all_any_none_of.html'),

            ('http://en.cppreference.com/w/cpp/ranges-placeholder/concepts/Assignable',
             'output/reference/en/cpp/experimental/ranges/concepts/View.html',
             'Assignable.html'),

            ('http://en.cppreference.com/w/cpp/ranges-placeholder/concepts/Assignable',
             'output/reference/en/cpp/experimental/ranges/View.html',
             'concepts/Assignable.html'),

            ('http://en.cppreference.com/w/cpp/ranges-placeholder/concepts/Assignable',
             'output/reference/en/cpp/experimental/ranges/range/View.html',
             '../concepts/Assignable.html'),

            ('http://en.cppreference.com/w/cpp/ranges-algorithm-placeholder/all_any_none_of',
             'output/reference/en/cpp/experimental/ranges/View.html',
             'algorithm/all_any_none_of.html'),

            ('http://en.cppreference.com/w/cpp/ranges-algorithm-placeholder/all_any_none_of',
             'output/reference/en/cpp/experimental/ranges/range/View.html',
             '../algorithm/all_any_none_of.html'),
        ]

        # transform_ranges_placeholder(target, file, root)
        #  target: the placeholder link
        #  file:   path of the file that contains the link
        #  root:   path to the site root (where '/' should link to)
        root = "output/reference"
        for target, file, expected in entries:
            self.assertEqual(expected, transform_ranges_placeholder(target, file, root),
                msg="target='{}', file='{}', root='{}'".format(target, file, root))

            target = target.replace('http://', 'https://')
            self.assertEqual(expected, transform_ranges_placeholder(target, file, root),
                msg="target='{}', file='{}', root='{}'".format(target, file, root))
