#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import re
import sys

if len(sys.argv) != 4:
    print "Wrong usage"
    print "First argument - source dot file"
    print "Second argument - settings dot file"
    print "Third argument - output dot file"
    sys.exit(-1)

inf = open(sys.argv[1], 'r')
setf = open(sys.argv[2], 'r')
outf = open(sys.argv[3], 'w')

itext = inf.read()
inf.close()

stext = setf.read()
setf.close()

# strip comments
stext = re.sub('\/\*.*?\*\/', '', stext, flags=re.MULTILINE)
stext = re.sub('^#.*$', '', stext)

# replace
itext = re.sub('@SETTINGS@', stext, itext)

outf.write(itext)
