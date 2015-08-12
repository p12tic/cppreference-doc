#!/usr/bin/env python3

#   Copyright (C) 2015  Michael Munzert <info@mm-log.com>
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

import os
import re
import shutil
import urllib.parse

from bs4 import BeautifulSoup

def urldecode(s):
    return urllib.parse.unquote(s)

def clean_faq(output_path):
    # Fix FAQ links
    shutil.move(os.path.join(output_path, 'reference/en/Cppreference:FAQ.html'), 
                os.path.join(output_path, 'reference/en/FAQ.html'))
    for fn in ['reference/en/c.html', 'reference/en/cpp.html']:
        with open(os.path.join(output_path, fn), 'rb') as f:
            soup = BeautifulSoup(f.read(), "lxml")

        for link in soup.find_all('a'):
            if link.text == 'FAQ':
                link['href'] = 'FAQ.html'
                break;

        with open(os.path.join(output_path, fn), 'wb') as f:
            f.write(soup.prettify('utf-8'))
            
    # clean FAQ.html        
    with open(os.path.join(output_path, 'reference/en/FAQ.html'), 'rb') as f:
        soup = BeautifulSoup(f.read(), "lxml")
        
    for link in soup.find_all('a'):
        try:
            href = link['href']
            if 'FAQ.html' in href:
                link['href'] = re.sub('([^#]*)', 'FAQ.html', href)
        except KeyError:
            pass

    navbar_head = soup.find(attrs={'class': 't-navbar-head'})
    navbar_head.a.string   = 'Index'
    navbar_head.a['href']  = 'index.html'
    navbar_head.a['title'] = 'index'
    navbar_head.div.extract()

    with open(os.path.join(output_path, 'reference/en/FAQ.html'), 'wb') as f:
        f.write(soup.prettify('utf-8'))
        
