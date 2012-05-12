#!/usr/bin/python

import pylab
import os

DATA = (
    (   'floor',
        (   (-3, -3, 'T'),
            (-2, -3, 'F'),
            (-2, -2, 'T'),
            (-1, -2, 'F'),
            (-1, -1, 'T'),
            ( 0, -1, 'F'),
            ( 0,  0, 'T'),
            ( 1,  0, 'F'),
            ( 1,  1, 'T'),
            ( 2,  1, 'F'),
            ( 2,  2, 'T'),
            ( 3,  2, 'F'),
            ( 3,  3, 'T'),
            ( 4,  3, 'F')
        )
    ),
    (   'ceil',
        (   (-4, -3, 'F'),
            (-3, -3, 'T'),
            (-3, -2, 'F'),
            (-2, -2, 'T'),
            (-2, -1, 'F'),
            (-1, -1, 'T'),
            (-1,  0, 'F'),
            ( 0,  0, 'T'),
            ( 0,  1, 'F'),
            ( 1,  1, 'T'),
            ( 1,  2, 'F'),
            ( 2,  2, 'T'),
            ( 2,  3, 'F'),
            ( 3,  3, 'T')
        )
    ),
    (   'trunc',
        (   (-4, -3, 'F'),
            (-3, -3, 'T'),
            (-3, -2, 'F'),
            (-2, -2, 'T'),
            (-2, -1, 'F'),
            (-1, -1, 'T'),
            (-1,  0, 'F'),
            ( 1,  0, 'F'),
            ( 1,  1, 'T'),
            ( 2,  1, 'F'),
            ( 2,  2, 'T'),
            ( 3,  2, 'F'),
            ( 3,  3, 'T'),
            ( 4,  3, 'F')
        )
    ),
    (   'round_away_zero',
        (   (-3.5, -3, 'F'),
            (-2.5, -3, 'T'),
            (-2.5, -2, 'F'),
            (-1.5, -2, 'T'),
            (-1.5, -1, 'F'),
            (-0.5, -1, 'T'),
            (-0.5,  0, 'F'),
            ( 0.5,  0, 'F'),
            ( 0.5,  1, 'T'),
            ( 1.5,  1, 'F'),
            ( 1.5,  2, 'T'),
            ( 2.5,  2, 'F'),
            ( 2.5,  3, 'T'),
            ( 3.5,  3, 'F'),
            ( 3.5,  4, 'T')
        )
    )
)

font = {'family' : 'DejaVu Serif',
        'weight' : 'normal',
        'size'   : 9}
        
pylab.rc('font', **font)

for i in xrange(len(DATA)):
    (name,idata) = DATA[i]
    
    fig = pylab.figure(figsize=(200.0/72.0,200.0/72.0))
    ax = fig.add_subplot(111)
    
    for j in xrange(len(idata)/2):
        (x1,y1,fill) = idata[j*2]
        (x2,y2,fill) = idata[j*2+1]
        x = (x1, x2)
        y = (y1, y2)
        l = ax.plot(x, y)
        pylab.setp(l, 'color', '#0000FF')
        pylab.setp(l, 'linewidth', 0.5)
        
    for j in xrange(len(idata)):
        (x,y,fill) = idata[j]

        l = ax.plot(x, y, marker='o')
        
        pylab.setp(l, 'markersize', 7.5)
        pylab.setp(l, 'markeredgewidth', 0.5)
        pylab.setp(l, 'markeredgecolor', '#0000FF')
        if fill == 'T':
            pylab.setp(l, 'markerfacecolor', '#0000FF')
        else:
            pylab.setp(l, 'markerfacecolor', 'white')

    ax.grid(True)
    ax.set_axisbelow(True)
    ax.tick_params(pad = 7.5)
    ax.set_aspect(1.0)
    ax.set_xlim((-3.5, 3.5))
    ax.set_ylim((-3.5, 3.5))

    outfile = 'output/math-' + name + '.svg'
    tmpfile = outfile + '.tmp'
    pylab.savefig(tmpfile, format='svg')
    os.system('xsltproc --novalid fix_svg-math.xsl ' + tmpfile + ' > ' + outfile)
    os.system('rm ' + tmpfile)

    pylab.close()
        
