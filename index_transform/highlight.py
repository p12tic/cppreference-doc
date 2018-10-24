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


class Index2Highlight(IndexTransform):
    def __init__(self, out_file):
        super().__init__()
        self.out_file = out_file

    def check_is_member(self, el):
        if el.getparent().tag == 'index':
            return False
        if el.tag == 'function':
            return True
        if el.tag == 'variable':
            return True
        if el.tag == 'constructor':
            return True
        if el.tag == 'destructor':
            return True
        return False

    def process_item_hook(self, el, full_name, full_link):
        if self.check_is_member(el):
            pass
        elif '<' in full_name:
            pass
        elif '>' in full_name:
            pass
        elif '(' in full_name:
            pass
        elif ')' in full_name:
            pass
        else:
            self.out_file.write(full_name + ' => ' + full_link + '\n')

        IndexTransform.process_item_hook(self, el, full_name, full_link)

    def inherits_worker(self, parent_name, pending, finished=list()):
        pass  # do not walk the inheritance hierarchy
