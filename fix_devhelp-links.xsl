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
                xmlns:devhelp="http://www.devhelp.net/book"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:str="http://exslt.org/strings"
                >

<xsl:output indent="yes"/>

<xsl:variable name="mapping" select="document('link-map.xml')/files/*"/>

<xsl:template match="node()|@*">
  <xsl:copy>
    <xsl:apply-templates select="node()|@*"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="@link">
  <xsl:attribute name="link">
    <xsl:choose>
      <xsl:when test="$mapping[@from = current()]">
        <xsl:value-of select="$mapping[@from = current()]/@to"/>
      </xsl:when>
      <xsl:otherwise>404</xsl:otherwise>
    </xsl:choose>
  </xsl:attribute>
</xsl:template>

</xsl:stylesheet>
