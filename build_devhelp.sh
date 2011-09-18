#!/bin/bash

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
