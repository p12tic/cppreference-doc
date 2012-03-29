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
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:str="http://exslt.org/strings"
                >
<xsl:import href="index_transform.xsl"/>

<xsl:template match="/index">
  <html>
  <head>
  <style type="text/css">
    body {
      font-size: 0.8em;
    }

    .link a {
      font-size: 0.8em;
      color: #808080;
    }
    .mark {
      font-size: 0.8em;
      color: #008000;
    }
  </style>
  </head>
  <body>
    <ul>
      <xsl:apply-templates mode="process-item" select="child::*"/>
    </ul>
  </body>
  </html>
</xsl:template>

<xsl:template name="process-item-finalize">
  <xsl:param name="name"/>
  <xsl:param name="link"/>
  <li>
    <xsl:call-template name="output-item">
      <xsl:with-param name="name" select="$name"/>
      <xsl:with-param name="link" select="$link"/>
    </xsl:call-template>

    <ul>
      <xsl:apply-templates mode="process-children" select=".">
        <xsl:with-param name="parent-name" select="$name"/>
        <xsl:with-param name="parent-link" select="$link"/>
      </xsl:apply-templates>
    </ul>
  </li>
</xsl:template>

<xsl:template name="output-item">
  <xsl:param name="name"/>
  <xsl:param name="link"/>
  
  <xsl:variable name="mark">
    <xsl:choose>
      <xsl:when test="name()='const'"><xsl:text>(const)</xsl:text></xsl:when>
      <xsl:when test="name()='function'"><xsl:text>(function)</xsl:text></xsl:when>
      <xsl:when test="name()='constructor'"><xsl:text>(function)</xsl:text></xsl:when>
      <xsl:when test="name()='destructor'"><xsl:text>(function)</xsl:text></xsl:when>
      <xsl:when test="name()='class'"><xsl:text>(class)</xsl:text></xsl:when>
      <xsl:when test="name()='enum'"><xsl:text>(enum)</xsl:text></xsl:when>
      <xsl:when test="name()='typedef'"><xsl:text>(typedef)</xsl:text></xsl:when>
      <xsl:when test="name()='specialization'"><xsl:text>(class)</xsl:text></xsl:when>
      <xsl:when test="name()='overload'"><xsl:text>(function)</xsl:text></xsl:when>
      <xsl:otherwise/>
    </xsl:choose>
  </xsl:variable>
  
  <tt><b><xsl:value-of select="$name"/></b></tt>
  [
  <span class="link">
    <a href="http://en.cppreference.com/w/{$link}">
      <xsl:value-of select="$link"/>
    </a>
  </span>
  ]
  <span class="mark"><xsl:value-of select="$mark"/></span>
</xsl:template>

</xsl:stylesheet>


