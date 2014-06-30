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

# copy the source tree
os.system('rm -rf output/reference')
os.system('mkdir -p output/reference')
os.system('cp -rt output/reference reference/*')

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
        os.system('cp -rl ' + src_data_path + '/* ' + data_path)
        os.system('rm -r ' + src_data_path)

    # also copy the custom fonts
    os.system('cp ' + path + 'DejaVuSansMonoCondensed60.ttf ' +
                      path + 'DejaVuSansMonoCondensed75.ttf ' + data_path)
    # remove what's left
    os.system('rm -r '+ path)


# find files that need to be renamed
files_rename_qs = []
files_rename_quot = []
files_loader = []
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

# find files that need to be preprocessed
html_files = []
for root, dirnames, filenames in os.walk('output/reference/'):
    for filename in fnmatch.filter(filenames, '*.html'):
        html_files.append(os.path.join(root, filename))

#temporary fix
r1 = re.compile('<style[^<]*?<[^<]*?MediaWiki:Geshi\.css[^<]*?<\/style>', re.MULTILINE)

# fix links to files in rename_map
rlink = re.compile('((?:src|href)=")([^"]*)(")')

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
    return pre + target + post

# clean the html files
for fn in html_files:
    f = open(fn, "r")
    text = f.read()
    f.close()

    text = r1.sub('', text);
    text = rlink.sub(rlink_fix, text)

    f = open(fn, "w")
    f.write(text)
    f.close()

    tmpfile = fn + '.tmp';
    ret = os.system('xsltproc --novalid --html --encoding UTF-8 preprocess.xsl "' + fn + '" > "' + tmpfile + '"')
    if ret != 0:
        print("FAIL: " + fn)
        continue
    os.system('mv "' + tmpfile + '" "' + fn + '"')

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

