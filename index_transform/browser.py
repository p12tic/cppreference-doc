'''
    Copyright (C) 2013  Povilas Kanapickas <povilas@radix.lt>
    Copyright (C) 2018  Monika Kairaityte <monika@kibit.lt>

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

from index_transform.common import IndexTransform
from xml_utils import xml_escape


class Index2Browser(IndexTransform):

    def __init__(self, out_file):
        super().__init__()
        self.out_file = out_file

    def output_item(self, el, full_name, full_link):
        tag_to_mark = {
            'const': '(const)',
            'function': '(function)',
            'constructor': '(function)',
            'destructor': '(function)',
            'class': '(class)',
            'enum': '(enum)',
            'variable': '(variable)',
            'typedef': '(typedef)',
            'specialization': '(class)',
            'overload': '(function)',
        }
        mark = ''
        if el.tag in tag_to_mark:
            mark = tag_to_mark[el.tag]

        res = u''
        res += '<tt><b>{0}</b></tt> [<span class="link">'.format(
            xml_escape(full_name))
        res += '<a href="http://en.cppreference.com/w/{0}">'.format(
            xml_escape(full_link))
        res += '{0}</a></span>] <span class="mark">{1}</span>\n'.format(
            full_link, mark)

        return res

    def process_item_hook(self, el, full_name, full_link):
        self.out_file.write('<li>' +
                            self.output_item(el, full_name, full_link) +
                            '<ul>')
        IndexTransform.process_item_hook(self, el, full_name, full_link)
        self.out_file.write('</ul></li>\n')
