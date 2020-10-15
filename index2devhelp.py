#!/usr/bin/env python3
'''
    Copyright (C) 2013  Povilas Kanapickas <povilas@radix.lt>

    This file is part of cppreference-doc

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see http://www.gnu.org/licenses/.
'''

import argparse

from index_transform.devhelp import transform_devhelp


def main():
    parser = argparse.ArgumentParser(prog='index2devhelp')
    parser.add_argument('book_base', type=str,
                        help='url to the location of the book')
    parser.add_argument('chapters_path', type=str,
                        help='path to the chapters file to include')
    parser.add_argument('book_title', type=str,
                        help='the title of the book')
    parser.add_argument('book_name', type=str,
                        help='the name of the package')
    parser.add_argument('rel_link', type=str,
                        help='the link relative to the root of the '
                             'documentation')
    parser.add_argument('in_fn', type=str,
                        help='the path of the source file')
    parser.add_argument('dest_fn', type=str,
                        help='the path of the destination file')
    args = parser.parse_args()

    with open(args.dest_fn, 'wb') as out_f:
        output = transform_devhelp(args.book_title, args.book_name,
                                   args.book_base, args.rel_link,
                                   args.chapters_path, args.in_fn)
        out_f.write(output)


if __name__ == '__main__':
    main()
