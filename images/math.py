#!/usr/bin/env python
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

import matplotlib.pyplot as plt
import os
from numpy import *
from bisect import *

#
# DATA - array of items describing data to plot
# Each item consists of the following parts
#
# 1 : string           : name of the function
# 2 : array of 4 items : xmin, xmax, ymin, ymax
# 3 : array of N items : X coordinates for the N points to plot.
#                        Points outside [xmin, xmax] won't be plotted
# 4 : array of N items : Y coordinates for the N points to plot.
#                        Points outside [ymin, ymax] won't be plotted
# 5 : array of M items : Points where the function is discontinuous.
#                        Each of the items contains 6 elements:
#                         * x,y of the beginning of the discontinuity region
#                         * 'T' or 'F' depending on whether the function has
#                           a real value at that point
#                         * x,y of the end of the discontinuity region
#                         * 'T' or 'F' depending on whether the function has
#                           a real value at that point
#

DATA = (
    (   'floor',
        ( -3.5, 3.5, -3.5, 3.5 ),
        arange(-4, 4, 0.02),
        floor(arange(-4, 4, 0.02)),
        (   (-3, -4, 'F', -3, -3, 'T'),
            (-2, -3, 'F', -2, -2, 'T'),
            (-1, -2, 'F', -1, -1, 'T'),
            ( 0, -1, 'F',  0,  0, 'T'),
            ( 1,  0, 'F',  1,  1, 'T'),
            ( 2,  1, 'F',  2,  2, 'T'),
            ( 3,  2, 'F',  3,  3, 'T')
        )
    ),
    (   'ceil',
        ( -3.5, 3.5, -3.5, 3.5 ),
        arange(-4, 4, 0.02),
        ceil(arange(-4, 4, 0.02)),
        (   (-3, -3, 'T', -3, -2, 'F'),
            (-2, -2, 'T', -2, -1, 'F'),
            (-1, -1, 'T', -1,  0, 'F'),
            ( 0,  0, 'T',  0,  1, 'F'),
            ( 1,  1, 'T',  1,  2, 'F'),
            ( 2,  2, 'T',  2,  3, 'F'),
            ( 3,  3, 'T',  3,  4, 'F')
        )
    ),
    (   'trunc',
        ( -3.5, 3.5, -3.5, 3.5 ),
        arange(-4, 4, 0.02),
        trunc(arange(-4, 4, 0.02)),
        (   (-3, -3, 'T', -3, -2, 'F'),
            (-2, -2, 'T', -2, -1, 'F'),
            (-1, -1, 'T', -1,  0, 'F'),
            ( 1,  0, 'F',  1,  1, 'T'),
            ( 2,  1, 'F',  2,  2, 'T'),
            ( 3,  2, 'F',  3,  3, 'T'),
        )
    ),
    (   'round_away_zero',
        ( -3.5, 3.5, -3.5, 3.5 ),
        arange(-4, 4, 0.02),
        around(arange(-4, 4, 0.02)),
        (   (-3.5, -4, 'T', -3.5, -3, 'F'),
            (-2.5, -3, 'T', -2.5, -2, 'F'),
            (-1.5, -2, 'T', -1.5, -1, 'F'),
            (-0.5, -1, 'T', -0.5,  0, 'F'),
            ( 0.5,  0, 'F',  0.5,  1, 'T'),
            ( 1.5,  1, 'F',  1.5,  2, 'T'),
            ( 2.5,  2, 'F',  2.5,  3, 'T'),
            ( 3.5,  3, 'F',  3.5,  4, 'T')
        )
    ),
    (   'sin',
        ( -6.3, 6.3, -1, 1),
        arange(-6.3, 6.3, 0.02),
        sin(arange(-6.3, 6.3, 0.02)),
        ()
    ),
    (   'cos',
        ( -6.3, 6.3, -1, 1),
        arange(-6.3, 6.3, 0.02),
        cos(arange(-6.3, 6.3, 0.02)),
        ()
    ),
    (   'tan',
        ( -6.3, 6.3, -4, 4),
        arange(-6.3, 6.3, 0.02),
        tan(arange(-6.3, 6.3, 0.02)),
        (   ( -4.72, 100, 'F',  -4.70, -100, 'F'),
            ( -1.59, 100, 'F',  -1.57, -100, 'F'),
            (  1.57, 100, 'F',   1.59, -100, 'F'),
            (  4.70, 100, 'F',   4.72, -100, 'F')
        )
    )
)

font = {'family' : 'DejaVu Sans',
        'weight' : 'normal',
        'size'   : 9}

plt.rc('font', **font)

for i in xrange(len(DATA)):
    (name,lim,xdata,ydata,discont) = DATA[i]

    #make a single array from the data
    data = list()
    for j in xrange(len(xdata)):
        data.append({'type' : 'c', 'x' : xdata[j], 'y' : ydata[j]})

    data.sort(key = lambda it: it['x'])

    for j in xrange(len(discont)):
        (x1,y1,t1, x2,y2,t2) = discont[j]

        data_x = [i['x'] for i in data]

        imin = bisect_left(data_x, x1)
        imax = bisect_right(data_x, x2)
        del data[imin:imax]

        data.insert(imin, {'type' : 'dend', 'x': x2, 'y' : y2, 't': t2 })
        data.insert(imin, {'type' : 'dbeg', 'x': x1, 'y' : y1, 't': t1 })

    # make fig
    fig = plt.figure(figsize=(200.0/72.0,200.0/72.0))
    ax = fig.add_subplot(111)

    (xmin,xmax,ymin,ymax) = lim
    ax.set_xlim((xmin, xmax))
    ax.set_ylim((ymin, ymax))

    # functions for range checking
    def c_in_lim(cx, cy, px, py):
        if cx < xmin and px < xmin:
            return False
        if cx > xmax and px > xmax:
            return False
        if cy < ymin and py < ymin:
            return False
        if cy > ymax and py > ymax:
            return False
        return True

    def d_in_lim(x, y):
        if x < xmin - (xmax-xmin)*0.03:
            return False
        if x > xmax + (xmax-xmin)*0.03:
            return False
        if y < ymin - (ymax-ymin)*0.03:
            return False
        if y > ymax + (ymax-ymin)*0.03:
            return False
        return True

    # paint lines

    # the lines are painted in batches
    paint_batch = list()
    for j in xrange(1, len(data)):

        prev_t = data[j-1]['type']
        curr_t = data[j]['type']
        prev_x = data[j-1]['x']
        curr_x = data[j]['x']
        prev_y = data[j-1]['y']
        curr_y = data[j]['y']

        is_good = True #whether current segment needs painting

        # don't paint out of bounds
        if curr_t == 'c':
            if not c_in_lim(curr_x, curr_y, prev_x, prev_y):
                is_good = False
        else:
            if not d_in_lim(curr_x, curr_y):
                is_good = False

        # don't paint within discontinuous region
        if (curr_t == 'dend' and prev_t == 'dbeg'):
            is_good = False

        # append an item to batch if needed
        if is_good:
            if len(paint_batch) == 0:
                paint_batch.append((prev_x, prev_y))
            paint_batch.append((curr_x, curr_y))

        # we need painting if this is the last data point
        if j == len(data) - 1:
            is_good = False

        # paint the current batch, if any
        if (not is_good) and len(paint_batch) > 1:

            # merge adjacent segments if they have the same direction
            def compute_dir(n):
                (x1,y1) = paint_batch[n]
                (x2,y2) = paint_batch[n+1]
                return (y2-y1)/(x2-x1)

            prev_dir = compute_dir(0)
            k = 1
            while k < len(paint_batch) - 1:
                curr_dir = compute_dir(k)
                if curr_dir == prev_dir:
                    del paint_batch[k]
                else:
                    prev_dir = curr_dir
                    k += 1

            # paint
            (x,y) = zip(*paint_batch)
            l = ax.plot(x, y)
            plt.setp(l, 'color', '#0000FF')
            plt.setp(l, 'linewidth', 0.5)
            paint_batch = []

    # paint markers
    for j in xrange(0, len(data)):
        curr_t = data[j]['type']
        curr_x = data[j]['x']
        curr_y = data[j]['y']

        # paint point marking discontinuous region if needed
        if curr_t != 'c':
            if not d_in_lim(curr_x, curr_y):
                continue

            fill = data[j]['t']
            l = ax.plot(curr_x, curr_y, marker='o')

            plt.setp(l, 'markersize', 7.5)
            plt.setp(l, 'markeredgewidth', 0.5)
            plt.setp(l, 'markeredgecolor', '#0000FF')
            if fill == 'T':
                plt.setp(l, 'markerfacecolor', '#0000FF')
            else:
                plt.setp(l, 'markerfacecolor', 'white')

    ax.grid(True)
    ax.set_axisbelow(True)
    ax.tick_params(pad = 7.5)
    ax.set_aspect((xmax-xmin)/(ymax-ymin)) # always produce square plots

    outfile = 'output/math-' + name + '.svg'
    tmpfile = outfile + '.tmp'
    plt.savefig(tmpfile, format='svg')
    os.system('xsltproc --novalid fix_svg-math.xsl ' + tmpfile + ' > ' + outfile)
    os.system('rm ' + tmpfile)

    plt.close()

