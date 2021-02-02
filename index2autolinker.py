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
import json

from index_transform.autolinker import Index2AutolinkerGroups
from index_transform.autolinker import Index2AutolinkerLinks


def main():
    ''' This script produces a definition file for AutoLinker extension

        The definitions are written in JSON in the following format:

        {
            "groups" : [
                {
                    name : "string",
                    OPTIONAL base_url : "string", END
                    urls : [ "url", "url", ... ],
                },
                ...
            ],
            "links" : [
                {
                    string : "string",
                    EITHER on_group : "name" OR on_page : "url" END
                    target : "url",
                },
                ...
            ],
        }
    '''
    parser = argparse.ArgumentParser(prog='index2autolinker')
    parser.add_argument('index', type=str,
                        help='Path to index file to process')
    parser.add_argument('destination', type=str,
                        help='Path to destination file to store results to')
    args = parser.parse_args()

    out_f = open(args.destination, 'w', encoding='utf-8')

    tr = Index2AutolinkerGroups()
    tr.transform_file(args.index)
    groups = tr.groups

    tr = Index2AutolinkerLinks()
    tr.transform_file(args.index)
    links = tr.links

    json_groups = list(groups.values())

    json_groups = sorted(json_groups, key=lambda x: x['name'])
    links = sorted(links, key=lambda x: x['target'])

    out_f.write(json.dumps({'groups': json_groups, 'links': links},
                           indent=None,
                           separators=(',\n', ': '), sort_keys=True))
    out_f.close()


if __name__ == '__main__':
    main()
