<?xml version="1.0" encoding="UTF-8"?>
<!--
    Copyright (C) 2012  Povilas Kanapickas <povilas@radix.lt>

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

<xsl:param name="qch-namespace" select="'cppreference.com'" />
<xsl:param name="qch-virtual-folder" select="'cpp'" />

<xsl:output indent="yes"/>

<xsl:template match="/devhelp:book">
  <QtHelpProject version="1.0">
    <namespace>
      <xsl:value-of select="concat($qch-namespace, '.', @name)" />
    </namespace>
    <virtualFolder>
      <xsl:value-of select="$qch-virtual-folder" />
    </virtualFolder>

    <customFilter name="{@title}">
      <filterAttribute>
        <xsl:value-of select="@name" />
      </filterAttribute>
    </customFilter>

    <filterSection>
      <filterAttribute>
        <xsl:value-of select="@name" />
      </filterAttribute>

      <toc>
        <section title="{@title}" ref="{@link}">
          <xsl:apply-templates select="devhelp:chapters/devhelp:sub" />
        </section>
      </toc>

      <keywords>
        <xsl:apply-templates select="devhelp:functions/devhelp:keyword" />
      </keywords>

      <files>
        <xsl:copy-of select="document('output/qch-files.xml')/files/*"/>
      </files>

    </filterSection>
  </QtHelpProject>
</xsl:template>

<xsl:template match="devhelp:sub">
  <section title="{@name}" ref="{@link}">
    <xsl:apply-templates select="devhelp:sub" />
  </section>
</xsl:template>

<xsl:template match="devhelp:keyword">
  <xsl:if test="@name != ''">
    <keyword name="{@name}" id="{@name}" ref="{@link}" />
  </xsl:if>
</xsl:template>

</xsl:stylesheet>


