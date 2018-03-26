#!/usr/bin/env python3

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

from premailer import transform
import os
import argparse
import multiprocessing

def main():

    parser = argparse.ArgumentParser(prog='preprocess_qch.py')
    parser.add_argument('--src', required = True, type=str,
            help='Source directory where raw website copy resides')
    parser.add_argument('--dst', required = True, type=str,
            help='Destination folder to put preprocessed archive to')
    args = parser.parse_args()

    source_root = str(args.src)
    dest_root = args.dst

    paths_list = []
    for root, dirs, files in os.walk(source_root):
        for file in files:
            if file.endswith(".html"):
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, source_root)
                dst_path = os.path.join(dest_root, rel_path)
                tuple = (src_path, dst_path)
                paths_list.append(tuple)

    count = 0
    for i, tuple in enumerate(paths_list, 1):
        src_path = tuple[0]
        dst_path = tuple[1]
        with open(src_path, 'r') as a_file:
            content = transform(a_file.read(), base_url=src_path)
            head = os.path.dirname(dst_path)
            os.makedirs(head, exist_ok=True)
            f = open(dst_path,"w")
            f.write(content)
            print('Processing file: {}/{}'.format(i, len(paths_list)))
             
if __name__ == "__main__":
    main()

