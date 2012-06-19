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
                xmlns:xlink="http://www.w3.org/1999/xlink"
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

<xsl:template match="//@xlink:href"/>
<xsl:template match="//@xlink:title"/>

<!--<xsl:template match="/svg:svg/@viewBox"/>-->

<xsl:template match="/svg:svg/svg:g/@transform">
  <xsl:attribute name="transform">
    <xsl:choose>
      <xsl:when test="contains(.,'scale(')">
        <xsl:variable name="before">
          <xsl:value-of select="substring-before(.,'scale(')"/>
        </xsl:variable>
        <xsl:variable name="after">
          <xsl:value-of select="substring-after(.,'scale(')"/>
        </xsl:variable>
        <xsl:variable name="after2">
          <xsl:value-of select="substring-after($after,')')"/>
        </xsl:variable>
        <xsl:value-of select="normalize-space(concat($before, $after2))"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="."/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:attribute>
</xsl:template>

</xsl:stylesheet>
