#!/bin/bash

#   Copyright (C) 2011  p12 <tir5c3@yahoo.co.uk>
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

page=$1

#replace a pseudo link in .devhelp2 with the actual link
pagename=$(cat "$page" | grep 'wgPageName' | awk -F\" '{print $(NF-1)}' )

if [ "x$pagename" != "x" ]
then
    #escape for consumption in sed
    link=$( echo "$pagename" | sed -e 's/\(\/\|\\\|&\)/\\&/g' )
    fixed_link=$( echo "$page" | sed -e 's/\(\.\|\/\|\*\|\[\|\]\|\\\)/\\&/g' )
    
    sed "s/link=\"$link\"/link=\"$fixed_link\"/g" -i ../cppreference-en-doc.devhelp2 
fi
