#!/usr/bin/env python3
'''
    Copyright (C) 2011-2014  Povilas Kanapickas <povilas@radix.lt>

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

xml_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

def xml_escape(text):
    return "".join(xml_escape_table.get(c,c) for c in text)

def xml_unescape(text):
    text = text.replace("&quot;", '"')
    text = text.replace("&apos;", "'")
    text = text.replace("&gt;", ">")
    text = text.replace("&lt;", "<")
    text = text.replace("&amp;", "&")
    return text
