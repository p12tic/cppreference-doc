#!/usr/bin/env python3

#   Copyright (C) 2017  Giedrius Zitkus <elink@namusauga.lt>
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


import argparse

from lxml import etree

from index_transform.devhelp_qch import convert_devhelp_to_qch


def main():
    parser = argparse.ArgumentParser(prog='devhelp2qch.py')
    parser.add_argument('--src', type=str,
                        help='The path to the XML input file')
    parser.add_argument('--dst', type=str,
                        help='The path to the destination XML file')
    parser.add_argument('--virtual_folder', type=str,
                        help='Virtual folder name')
    parser.add_argument('--file_list', type=str,
                        help='The path to the file list in XML file')
    args = parser.parse_args()

    src_path = args.src
    dst_path = args.dst
    v_folder = args.virtual_folder
    file_path = args.file_list

    parser = etree.XMLParser(encoding='UTF-8', recover=True)
    in_tree = etree.parse(src_path, parser)
    file_tree = etree.parse(file_path, parser)

    out_f = open(dst_path, 'wb')
    out_f.write(convert_devhelp_to_qch(in_tree.getroot(), file_tree.getroot(),
                                       v_folder))
    out_f.close()


if __name__ == "__main__":
    main()
