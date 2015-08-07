#!/usr/bin/env python3

#   Copyright (C) 2011, 2012  Povilas Kanapickas <povilas@radix.lt>
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

import fnmatch
import re
import os
import sys
import shutil
import urllib.parse
from xml_utils import xml_escape, xml_unescape
from bs4 import BeautifulSoup
from build_link_map import build_link_map

# copy the source tree
os.system('rm -rf output/reference')
os.system('mkdir -p output/reference')
os.system('cp -r reference/* output/reference ')

# rearrange the archive {root} here is output/reference

# before
# {root}/en.cppreference.com/w/ : html
# {root}/en.cppreference.com/mwiki/ : data
# {root}/en.cppreference.com/ : data
# ... (other languages)
# {root}/upload.cppreference.com/mwiki/ : data

# after
# {root}/common/ : all common data
# {root}/en/ : html for en
# ... (other languages)

data_path = "output/reference/common"
os.system('mkdir ' + data_path)
os.system('mv output/reference/upload.cppreference.com/mwiki/* ' + data_path)
os.system('rm -r output/reference/upload.cppreference.com/')

for lang in ["en"]:
    path = "output/reference/" + lang + ".cppreference.com/"
    src_html_path = path + "w/"
    src_data_path = path + "mwiki/"
    html_path = "output/reference/" + lang

    if (os.path.isdir(src_html_path)):
        os.system('mv ' + src_html_path + ' ' + html_path)

    if (os.path.isdir(src_data_path)):
        # the skin files should be the same for all languages thus we
        # can merge everything
        os.system('cp -r ' + src_data_path + '/* ' + data_path)
        os.system('rm -r ' + src_data_path)

    # also copy the custom fonts
    os.system('cp ' + path + 'DejaVuSansMonoCondensed60.ttf ' +
                      path + 'DejaVuSansMonoCondensed75.ttf ' + data_path)
    # remove what's left
    os.system('rm -r '+ path)


# find files that need to be renamed
files_rename_qs = []        # remove query string
files_rename_quot = []      # remove quotes
files_loader = []           # files served by load.php
for root, dirnames, filenames in os.walk('output/reference/'):
    for filename in fnmatch.filter(filenames, '*[?]*'):
        files_rename_qs.append((root, filename))
    for filename in fnmatch.filter(filenames, '*"*'):
        files_rename_quot.append((root, filename))
    for filename in fnmatch.filter(filenames, 'load.php[?]*'):
        files_loader.append((root, filename))

for root,fn in files_loader:
    files_rename_qs.remove((root,fn))

# strip query strings from filenames to support Windows filesystems
rename_map = []
def rename_file(root, fn, new_fn):
    path = os.path.join(root,fn)
    if not os.path.isfile(path):
        print("Not renaming " + path)
        return
    new_path = os.path.join(root,new_fn)
    shutil.move(path, new_path)
    rename_map.append((fn, new_fn))

for root,fn in files_rename_qs:
    rename_file(root, fn, re.sub('\?.*', '', fn))
for root,fn in files_rename_quot:
    rename_file(root, fn, re.sub('"', '_q_', fn))

# map loader names to more recognizable names
for root,fn in files_loader:
    if re.search("modules=site&only=scripts", fn):
        new_fn = "site_scripts.js"
    elif re.search("modules=site&only=styles", fn):
        new_fn = "site_modules.css"
    elif re.search("modules=skins.*&only=scripts", fn):
        new_fn = "skin_scripts.js"
    elif re.search("modules=startup&only=scripts", fn):
        new_fn = "startup_scripts.js"
    elif re.search("modules=.*ext.*&only=styles", fn):
        new_fn = "ext.css"
    else:
        print("Loader file " + fn + " does not match any known files")
        sys.exit(1)

    rename_file(root, fn, new_fn)

# rename filenames that conflict on case-insensitive filesystems
# TODO: perform this automatically
rename_file('output/reference/en/cpp/numeric/math', 'NAN.html', 'NAN.2.html')
rename_file('output/reference/en/c/numeric/math', 'NAN.html', 'NAN.2.html')

# generate link map as long as there is all information present
build_link_map()

# find files that need to be preprocessed
html_files = []
for root, dirnames, filenames in os.walk('output/reference/'):
    for filename in fnmatch.filter(filenames, '*.html'):
        html_files.append(os.path.join(root, filename))

#temporary fix
# r1 = re.compile('<style[^<]*?<[^<]*?MediaWiki:Geshi\.css[^<]*?<\/style>', re.MULTILINE)

# fix links to files in rename_map
rlink = re.compile('((?:src|href)=")([^"]*)(")')

html_comment = re.compile("<!--(.|\s)*?-->")

def rlink_fix(match):
    pre = match.group(1)
    target = match.group(2)
    post = match.group(3)

    target = xml_unescape(target)
    target = urllib.parse.unquote(target)
    for fn,new_fn in rename_map:
        target = target.replace(fn, new_fn)
    target = target.replace('../../upload.cppreference.com/mwiki/','../common/')
    target = target.replace('../mwiki/','../common/')
    target = re.sub('(\.php|\.css)\?.*', '\\1', target)
    target = urllib.parse.quote(target)
    target = xml_escape(target)
    target = target.replace('%23', '#');
    return pre + target + post


# clean the html files
bad_classes = {"noprint", "editsection", "printfooter", "catlinks"}

count = len(html_files)
for idx, fn in enumerate(html_files):
    if idx % 50 == 0:
        print("{} of {}".format(idx, count))
    with open(fn, 'r') as f:
        text = f.read()

    # text = r1.sub('', text);
    text = html_comment.sub('', text);
    text = rlink.sub(rlink_fix, text)
    soup = BeautifulSoup(text, "lxml")

    bad = []
    for tag in soup():
        tag_name = tag.name
        if tag_name == "script":
            bad.append(tag)
        elif tag_name == "link" and not "stylesheet" in tag["rel"]:
            bad.append(tag)
        elif tag_name == "style":
            try:
                if "text/css" not in tag["type"]:
                    bad.append(tag)
            except KeyError:
                bad.append(tag)
        elif tag_name == "meta" and tag.has_attr("content"):
            bad.append(tag)
        elif tag_name == "a" and tag.has_attr("title") and tag["title"] == "About this image":
            bad.append(tag.parent)
        else:
            try:
                if len(bad_classes.intersection(tag["class"])):
                    bad.append(tag)
            except KeyError:
                pass

    [s.extract() for s in bad]

    with open(fn, 'w') as f:
        f.write(soup.prettify())


# append css modifications

f = open("preprocess-css.css", "r")
css_app = f.read()
f.close()
f = open("output/reference/common/site_modules.css", "a")
f.write(css_app)
f.close()

# fix css files

for fn in [ "output/reference/common/site_modules.css",
            "output/reference/common/ext.css"]:
    f = open(fn, "r")
    text = f.read()
    f.close()

    # note that query string is not used in css files

    text = text.replace('../DejaVuSansMonoCondensed60.ttf', 'DejaVuSansMonoCondensed60.ttf')
    text = text.replace('../DejaVuSansMonoCondensed75.ttf', 'DejaVuSansMonoCondensed75.ttf')

    # QT Help viewer doesn't understand nth-child
    text = text.replace('nth-child(1)', 'first-child')

    f = open(fn, "w")
    f.write(text)
    f.close()

