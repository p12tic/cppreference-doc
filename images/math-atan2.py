#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Copyright (C) 2011, 2012  p12 <tir5c3@yahoo.co.uk>
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

import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt

import os
import numpy as np
import math
import pprint

font = {'family' : 'DejaVu Sans',
        'weight' : 'normal',
        'size'   : 18}

plt.rc('font', **font)
plt.rc('contour', **{ 'negative_linestyle' : 'solid'})

# generate data
X = np.arange(-1, 1.05, 0.02)
Y = np.arange(-1, 1.05, 0.02)
X, Y = np.meshgrid(X, Y)
Z = np.arctan2(Y,X)

# generate labels
levels = [-math.pi*3/4, -math.pi*2/4, -math.pi/4,
          0, math.pi/4, math.pi/2, math.pi*3/4 ]
labels = [u'-3/4 π', u'-1/2 π', u'-1/4 π', '0', u'1/4 π', u'1/2 π', u'3/4 π' ]

fmt = {}
for l,s in zip( levels, labels ):
    fmt[l] = s

# generate plot
fig = plt.figure(figsize=(475.0/72.0,400.0/72.0))
ax = fig.add_subplot(111)

ct = ax.contour(X, Y, Z, levels=levels, linewidths=0.5, colors='k')
ax.clabel(ct, fmt=fmt, colors = '#000000', fontsize=14)

# HACK - remove the contour label at discontinuity of atan2
ct.labelTexts[5].set_text('')

pc = ax.pcolor(X, Y, Z, cmap=plt.get_cmap("Spectral_r"), vmin=-3.2, vmax=3.2)
fig.colorbar(pc)

ax.set_xlim((-1.0, 1.0))
ax.set_ylim((-1.0, 1.0))
ax.set_axisbelow(True)
ax.tick_params(pad = 15)
ax.set_aspect(1.0)

fig.savefig('output/math-atan2.png')

plt.close()
