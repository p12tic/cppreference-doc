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
import io
from lxml import etree
import re
import os
import sys
import shutil
import urllib.parse
from xml_utils import xml_escape, xml_unescape

def rmtree_if_exists(dir):
    if os.path.isdir(dir):
        shutil.rmtree(dir)

def move_dir_contents_to_dir(srcdir, dstdir):
    for fn in os.listdir(srcdir):
        shutil.move(os.path.join(srcdir, fn),
                    os.path.join(dstdir, fn))

def rearrange_archive(root):
    # rearrange the archive. {root} here is output/reference

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

    data_path = os.path.join(root, 'common')
    rmtree_if_exists(data_path)
    shutil.move(os.path.join(root, 'upload.cppreference.com/mwiki'), data_path)
    shutil.rmtree(os.path.join(root, 'upload.cppreference.com'))

    for lang in ["en"]:
        path = os.path.join(root, lang + ".cppreference.com/")
        src_html_path = path + "w/"
        src_data_path = path + "mwiki/"
        html_path = os.path.join(root, lang)

        if os.path.isdir(src_html_path):
            shutil.move(src_html_path, html_path)

        if os.path.isdir(src_data_path):
            # the skin files should be the same for all languages thus we
            # can merge everything
            move_dir_contents_to_dir(src_data_path, data_path)

        # also copy the custom fonts
        shutil.copy(os.path.join(path, 'DejaVuSansMonoCondensed60.ttf'), data_path)
        shutil.copy(os.path.join(path, 'DejaVuSansMonoCondensed75.ttf'), data_path)

        # remove what's left
        shutil.rmtree(path)

    # remove the XML source file
    for fn in fnmatch.filter(os.listdir(root), 'cppreference-export*.xml'):
        os.remove(os.path.join(root, fn))

def add_file_to_rename_map(rename_map, dir, fn, new_fn):
    path = os.path.join(dir, fn)
    if not os.path.isfile(path):
        print("ERROR: Not renaming '{0}' because path does not exist".format(path))
        return
    rename_map.append((dir, fn, new_fn))

# Converts complex URL to resources supplied by MediaWiki loader to a simplified
# name
def convert_loader_name(fn):
    if "modules=site&only=scripts" in fn:
        return "site_scripts.js"
    elif "modules=site&only=styles" in fn:
        return "site_modules.css"
    elif "modules=startup&only=scripts" in fn:
        return "startup_scripts.js"
    elif re.search("modules=skins.*&only=scripts", fn):
        return "skin_scripts.js"
    elif re.search("modules=.*ext.*&only=styles", fn):
        return "ext.css"
    else:
        raise Exception('Loader file {0} does not match any known files'.format(fn))

def find_files_to_be_renamed(root):
    # Returns a rename map: array of tuples each of which contain three strings:
    # the directory the file resides in, the source and destination filenames.

    # The rename map specifies files to be renamed in order to support them on
    # windows filesystems which don't support certain characters in file names
    rename_map = []

    files_rename = []           # general files to be renamed
    files_loader = []           # files served by load.php. These should map to
                                # consistent and short file names because we
                                # modify some of them later in the pipeline

    for dir, _, filenames in os.walk(root):
        filenames_loader = set(fnmatch.filter(filenames, 'load.php[?]*'))
        # match any filenames with '?"*' characters
        filenames_rename = set(fnmatch.filter(filenames, '*[?"*]*'))

        # don't process load.php files in general rename handler
        filenames_rename -= filenames_loader

        for fn in filenames_loader:
            files_loader.append((dir, fn))
        for fn in filenames_rename:
            files_rename.append((dir, fn))

    for dir, orig_fn in files_rename:
        fn = orig_fn
        fn = re.sub(r'\?.*', '', fn)
        fn = fn.replace('"', '_q_')
        fn = fn.replace('*', '_star_')
        add_file_to_rename_map(rename_map, dir, orig_fn, fn)

    # map loader names to more recognizable names
    for dir, fn in files_loader:
        new_fn = convert_loader_name(fn)
        add_file_to_rename_map(rename_map, dir, fn, new_fn)

    # rename filenames that conflict on case-insensitive filesystems
    # TODO: perform this automatically
    add_file_to_rename_map(rename_map, os.path.join(root, 'en/cpp/numeric/math'), 'NAN.html', 'NAN.2.html')
    add_file_to_rename_map(rename_map, os.path.join(root, 'en/c/numeric/math'), 'NAN.html', 'NAN.2.html')
    return rename_map

def rename_files(rename_map):
    for dir, old_fn, new_fn in rename_map:
        src_path = os.path.join(dir, old_fn)
        dst_path = os.path.join(dir, new_fn)
        print("Renaming '{0}' to \n         '{1}'".format(src_path, dst_path))
        shutil.move(src_path, dst_path)

def find_html_files(root):
    # find files that need to be preprocessed
    html_files = []
    for dir, _, filenames in os.walk(root):
        for filename in fnmatch.filter(filenames, '*.html'):
            html_files.append(os.path.join(dir, filename))
    return html_files

def is_loader_link(target):
    if re.match(r'https?://[a-z]+\.cppreference\.com/mwiki/load\.php', target):
        return True
    return False

def transform_loader_link(target, file, root):
    # Absolute loader.php links need to be made relative
    abstarget = os.path.join(root, "common/" + convert_loader_name(target))
    return os.path.relpath(abstarget, os.path.dirname(file))

def is_ranges_placeholder(target):
    if re.match(r'https?://[a-z]+\.cppreference\.com/w/cpp/ranges(-[a-z]+)?-placeholder/.+', target):
        return True
    return False

def transform_ranges_placeholder(target, file, root):
    # Placeholder link replacement is implemented in the MediaWiki site JS at
    # https://en.cppreference.com/w/MediaWiki:Common.js

    ranges = 'cpp/experimental/ranges' in file
    repl = (r'\1/cpp/experimental/ranges/\2' if ranges else r'\1/cpp/\2')

    if 'ranges-placeholder' in target:
        match = r'https?://([a-z]+)\.cppreference\.com/w/cpp/ranges-placeholder/(.+)'
    else:
        match = r'https?://([a-z]+)\.cppreference\.com/w/cpp/ranges-([a-z]+)-placeholder/(.+)'
        repl += (r'/\3' if ranges else r'/ranges/\3')

    # Turn absolute placeholder link into site-relative link
    reltarget = re.sub(match, repl + '.html', target)

    # Make site-relative link file-relative
    abstarget = os.path.join(root, reltarget)
    return os.path.relpath(abstarget, os.path.dirname(file))

def is_external_link(target):
    external_link_patterns = [
        'http://',
        'https://',
        'ftp://'
    ]
    for pattern in external_link_patterns:
        if target.startswith(pattern):
            return True
    return False

def trasform_relative_link(rename_map, target):
    target = urllib.parse.unquote(target)
    for _, fn, new_fn in rename_map:
        target = target.replace(fn, new_fn)
    target = target.replace('../../upload.cppreference.com/mwiki/','../common/')
    target = target.replace('../mwiki/','../common/')
    target = re.sub(r'(\.php|\.css)\?.*', r'\1', target)
    target = urllib.parse.quote(target)
    target = target.replace('%23', '#')
    return target

# Transforms a link in the given file according to rename map.
# target is the link to transform.
# file is the path of the file the link came from.
# root is the path to the root of the archive.
def transform_link(rename_map, target, file, root):
    if is_loader_link(target):
        return transform_loader_link(target, file, root)

    if is_ranges_placeholder(target):
        return transform_ranges_placeholder(target, file, root)

    if is_external_link(target):
        return target

    return trasform_relative_link(rename_map, target)

def has_class(el, *classes_to_check):
    value = el.get('class')
    if value is None:
        return False
    classes = value.split(' ')
    for cl in classes_to_check:
        if cl != '' and cl in classes:
            return True
    return False

# remove non-printable elements
def remove_noprint(html):
    for el in html.xpath('//*'):
        if has_class(el, 'noprint', 'editsection'):
            el.getparent().remove(el)
        elif el.get('id') in ['toc', 'catlinks']:
            el.getparent().remove(el)

# remove see also links between C and C++ documentations
def remove_see_also(html):
    for el in html.xpath('//tr[@class]'):
        if not has_class(el, 't-dcl-list-item', 't-dsc'):
            continue

        child_tds = el.xpath('.//td/div[@class]')
        if not any(has_class(td, 't-dcl-list-see', 't-dsc-see') for td in child_tds):
            continue

        # remove preceding separator, if any
        prev = el.getprevious()
        if prev is not None:
            child_tds = prev.xpath('.//td[@class]')
            if any(has_class(td, 't-dcl-list-sep') for td in child_tds):
                prev.getparent().remove(prev)

        el.getparent().remove(el)

    for el in html.xpath('//h3'):
        if len(el.xpath(".//span[@id = 'See_also']")) == 0:
            continue

        next = el.getnext()
        if next is None:
            el.getparent().remove(el)
        elif next.tag == 'table' and has_class(next, 't-dcl-list-begin') and len(next.xpath('.//tr')) == 0:
            el.getparent().remove(el)
            next.getparent().remove(next)

# remove Google Analytics scripts
def remove_google_analytics(html):
    for el in html.xpath('/html/body/script'):
        if el.get('src') is not None and 'google-analytics.com/ga.js' in el.get('src'):
            el.getparent().remove(el)
        elif el.text is not None and ('google-analytics.com/ga.js' in el.text or 'pageTracker' in el.text):
            el.getparent().remove(el)

# remove Carbon ads
def remove_ads(html):
    for el in html.xpath('//script[@src]'):
        if 'carbonads.com/carbon.js' in el.get('src'):
            el.getparent().remove(el)
    for el in html.xpath('/html/body/style'):
        if el.text is not None and '#carbonads' in el.text:
            el.getparent().remove(el)

def preprocess_html_file(root, fn, rename_map):
    parser = etree.HTMLParser()
    html = etree.parse(fn, parser)
    output = io.StringIO()

    # remove external links to unused resources
    for el in html.xpath('/html/head/link'):
        if el.get('rel') in [ 'alternate', 'search', 'edit', 'EditURI' ]:
            el.getparent().remove(el)

    remove_noprint(html)
    remove_see_also(html)
    remove_google_analytics(html)
    remove_ads(html)

    # apply changes to links caused by file renames
    for el in html.xpath('//*[@src or @href]'):
        if el.get('src') is not None:
            el.set('src', transform_link(rename_map, el.get('src'), fn, root))
        elif el.get('href') is not None:
            el.set('href', transform_link(rename_map, el.get('href'), fn, root))

    for err in parser.error_log:
        print("HTML WARN: {0}".format(err), file=output)

    html.write(fn, encoding='utf-8', method='html')
    return output.getvalue()

def preprocess_css_file(fn):
    f = open(fn, "r", encoding='utf-8')
    text = f.read()
    f.close()

    # note that query string is not used in css files

    text = text.replace('../DejaVuSansMonoCondensed60.ttf', 'DejaVuSansMonoCondensed60.ttf')
    text = text.replace('../DejaVuSansMonoCondensed75.ttf', 'DejaVuSansMonoCondensed75.ttf')

    # QT Help viewer doesn't understand nth-child
    text = text.replace('nth-child(1)', 'first-child')

    f = open(fn, "w", encoding='utf-8')
    f.write(text)
    f.close()
