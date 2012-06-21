<?xml version="1.0" encoding="UTF-8"?>
<!--
    Copyright (C) 2012  p12 <tir5c3@yahoo.co.uk>

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
-->
<xsl:stylesheet version="1.0"
                xmlns="http://www.w3.org/2000/svg"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:str="http://exslt.org/strings"
                xmlns:svg="http://www.w3.org/2000/svg"
                >
<xsl:output indent="yes"
            method="xml"
            encoding="UTF-8"
            standalone="no"
            doctype-public="-//W3C//DTD SVG 1.1//EN"
            doctype-system="http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"/>

<xsl:template match="node()|@*">
  <xsl:copy>
     <xsl:apply-templates select="node()|@*"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="/svg:svg/@width">
  <xsl:attribute name="width">
     <xsl:value-of select="str:replace(.,'pt','px')"/>
  </xsl:attribute>
</xsl:template>

<xsl:template match="/svg:svg/@height">
  <xsl:attribute name="height">
     <xsl:value-of select="str:replace(.,'pt','px')"/>
  </xsl:attribute>
</xsl:template>

</xsl:stylesheet>
