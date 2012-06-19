<?xml version="1.0" encoding="UTF-8"?>
<!--
    Copyright (C) 2011  p12 <tir5c3@yahoo.co.uk>

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
                xmlns="http://www.devhelp.net/book"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                >
<xsl:import href="index_transform.xsl"/>
<xsl:param name="book-base" select="'/usr/share/doc/cppreference-doc-en/html'"/>
<xsl:param name="chapters-file" select="''"/>
<xsl:param name="title" select="''"/>
<xsl:param name="name" select="''"/>

<xsl:output indent="yes"/>

<xsl:template match="/index">
  <book title="{$title}" name="{$name}"
        base="{$book-base}" link="cpp" version="2" language="c++">
    <xsl:copy-of select="document($chapters-file)"/>
    <functions>
      <xsl:apply-templates mode="process-item" select="child::*"/>
    </functions>
  </book>
</xsl:template>

<xsl:template name="output-item">
  <xsl:param name="name"/>
  <xsl:param name="link"/>

  <xsl:variable name="mark">
    <xsl:choose>
      <xsl:when test="name()='const'"><xsl:text>macro</xsl:text></xsl:when>
      <xsl:when test="name()='function'"><xsl:text>function</xsl:text></xsl:when>
      <xsl:when test="name()='constructor'"><xsl:text>function</xsl:text></xsl:when>
      <xsl:when test="name()='destructor'"><xsl:text>function</xsl:text></xsl:when>
      <xsl:when test="name()='class'"><xsl:text>class</xsl:text></xsl:when>
      <xsl:when test="name()='enum'"><xsl:text>enum</xsl:text></xsl:when>
      <xsl:when test="name()='typedef'"><xsl:text>typedef</xsl:text></xsl:when>
      <xsl:when test="name()='specialization'"><xsl:text>class</xsl:text></xsl:when>
      <xsl:when test="name()='overload'"><xsl:text>function</xsl:text></xsl:when>
      <xsl:otherwise/>
    </xsl:choose>
  </xsl:variable>

  <keyword type="{$mark}" name="{$name}" link="{$link}"/>
</xsl:template>

</xsl:stylesheet>


