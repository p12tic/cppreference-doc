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

from index_transform.browser import Index2Browser


def main():
    parser = argparse.ArgumentParser(prog='index2browser')
    parser.add_argument('index', type=str,
                        help='Path to index file to process')
    parser.add_argument('destination', type=str,
                        help='Path to destination file to store results to')
    args = parser.parse_args()

    out_f = open(args.destination, 'w', encoding='utf-8')

    out_f.write('''
<html>
  <head>
  <style type="text/css">
    body {
      font-size: 0.8em;
    }

    .link a {
      font-size: 0.8em;
      color: #808080;
    }
    .mark {
      font-size: 0.8em;
      color: #008000;
    }
  </style>
  </head>
  <body>
    <ul>
''')

    tr = Index2Browser(out_f)
    tr.transform_file(args.index)

    out_f.write('''
    </ul>
  </body>
</html>
''')


if __name__ == '__main__':
    main()
