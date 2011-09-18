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
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns="http://www.devhelp.net/book"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                >
<xsl:param name="book-base" select="'/usr/share/doc/cppreference-doc-en/'"/>

<xsl:output indent="yes"/>

<xsl:template match="/index">
  <book title="C++ Standard Library Reference Manual" name="cppreference-doc-en" 
        base="{$book-base}" link="cpp" version="2" language="c++">
    <xsl:copy-of select="document('index-chapters.xml')"/>
    <functions>
      <xsl:apply-templates select="child::*"/>
    </functions>
  </book>
</xsl:template>

<!--
  Main processing template
  Computes the full (with namespace/class prefix) name and absolute link
  Calls other templates to do the actual processing. Each of these templates can be exploited as an
      customization point
    mode="process-name" - returns the name for the identifier
    mode="process-link" - returns the relative link for the identifier
    mode="process-full-name" - composes full name of the identifier
    mode="process-full-link" - composes absolute link to the identifier
    mode="process-mark" - returns mark for the element
    mode="process-children" - processes children
-->
<xsl:template match="const|function|class|enum|typedef|constructor|destructor">

  <xsl:param name="parent-name" select="''"/>
  <xsl:param name="parent-link" select="''"/>

  <xsl:variable name="name">
    <xsl:apply-templates mode="process-name" select="."/>
  </xsl:variable>

  <xsl:variable name="link">
    <xsl:apply-templates mode="process-link" select="."/>
  </xsl:variable>

  <xsl:variable name="full-name">
    <xsl:apply-templates mode="process-full-name" select=".">
      <xsl:with-param name="name" select="$name"/>
      <xsl:with-param name="parent-name" select="$parent-name"/>
    </xsl:apply-templates>
  </xsl:variable>

  <xsl:variable name="full-link">
    <xsl:apply-templates mode="process-full-link" select=".">
      <xsl:with-param name="link" select="$link"/>
      <xsl:with-param name="parent-link" select="$parent-link"/>
    </xsl:apply-templates>
  </xsl:variable>

  <xsl:variable name="mark">
    <xsl:apply-templates mode="process-mark" select="."/>
  </xsl:variable>

  <xsl:call-template name="output-identifier">
    <xsl:with-param name="name" select="$full-name"/>
    <xsl:with-param name="link" select="$full-link"/>
    <xsl:with-param name="mark" select="$mark"/>
  </xsl:call-template>

  <xsl:apply-templates mode="process-children" select=".">
    <xsl:with-param name="parent-name" select="$full-name"/>
    <xsl:with-param name="parent-link" select="$full-link"/>
  </xsl:apply-templates>
</xsl:template>

<!--=====================================================================-->
<!-- process-name -->
<xsl:template mode="process-name" match="*">
  <xsl:value-of select="@name"/>
</xsl:template>

<!--=====================================================================-->
<!-- process-link -->
<xsl:template mode="process-link" match="*">
  <xsl:choose>
    <xsl:when test="@link='.'"/>
    <xsl:when test="@link"><xsl:value-of select="@link"/></xsl:when>
    <xsl:otherwise><xsl:value-of select="@name"/></xsl:otherwise>
  </xsl:choose>
</xsl:template>

<!--=====================================================================-->
<!-- process-full-name -->
<xsl:template mode="process-full-name" match="*">
  <xsl:param name="name" select="''"/>
  <xsl:param name="parent-name" select="''"/>

  <xsl:value-of select="$parent-name"/>
  <xsl:if test="$parent-name"><xsl:text>::</xsl:text></xsl:if>
  <xsl:value-of select="$name"/>
</xsl:template>


<xsl:template mode="process-full-name" match="constructor">
  <xsl:param name="parent-name" select="''"/>

  <xsl:value-of select="$parent-name"/>
  <xsl:if test="$parent-name"><xsl:text>::</xsl:text></xsl:if>

  <xsl:call-template name="get-last-item">
    <xsl:with-param name="string" select="$parent-name"/>
    <xsl:with-param name="sep" select="'::'"/>
  </xsl:call-template>
</xsl:template>


<xsl:template mode="process-full-name" match="destructor">
  <xsl:param name="parent-name" select="''"/>

  <xsl:value-of select="$parent-name"/>
  <xsl:if test="$parent-name"><xsl:text>::</xsl:text></xsl:if>
  <xsl:text>~</xsl:text>

  <xsl:call-template name="get-last-item">
    <xsl:with-param name="string" select="$parent-name"/>
    <xsl:with-param name="sep" select="'::'"/>
  </xsl:call-template>
</xsl:template>

<!--=====================================================================-->
<!-- process-full-link -->
<xsl:template mode="process-full-link" match="*">
  <xsl:param name="link" select="''"/>
  <xsl:param name="parent-link" select="''"/>

  <xsl:value-of select="$parent-link"/>
    <xsl:if test="string($parent-link) and string($link)"><xsl:text>/</xsl:text></xsl:if>
  <xsl:value-of select="$link"/>
</xsl:template>


<xsl:template mode="process-full-link" match="typedef">
  <xsl:param name="link" select="''"/>
  <xsl:param name="parent-link" select="''"/>

  <xsl:variable name="alias" select="@alias"/>
  <xsl:variable name="target" select="(/index/class[@name = $alias] |
                                       /index/enum[@name = $alias])[1]"/>

  <xsl:variable name="target-link">
    <xsl:apply-templates mode="process-link" select="$target"/>
  </xsl:variable>

  <xsl:choose>
    <xsl:when test="$alias and $target">
      <xsl:value-of select="$target-link"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$parent-link"/>
        <xsl:if test="string($parent-link) and string($link)"><xsl:text>/</xsl:text></xsl:if>
      <xsl:value-of select="$link"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template mode="process-full-link" match="constructor">
  <xsl:param name="parent-link" select="''"/>

  <xsl:value-of select="$parent-link"/>
  <xsl:if test="string($parent-link)"><xsl:text>/</xsl:text></xsl:if>

  <xsl:call-template name="get-last-item">
    <xsl:with-param name="string" select="$parent-link"/>
    <xsl:with-param name="sep" select="'/'"/>
  </xsl:call-template>
</xsl:template>


<xsl:template mode="process-full-link" match="destructor">
  <xsl:param name="parent-link" select="''"/>

  <xsl:value-of select="$parent-link"/>
  <xsl:if test="string($parent-link)"><xsl:text>/</xsl:text></xsl:if>

  <xsl:call-template name="get-last-item">
    <xsl:with-param name="string" select="$parent-link"/>
    <xsl:with-param name="sep" select="'/'"/>
  </xsl:call-template>
</xsl:template>

<!--=====================================================================-->
<!-- process-mark -->
<xsl:template mode="process-mark" match="const">
  <xsl:text>macro</xsl:text>
</xsl:template>

<xsl:template mode="process-mark" match="function">
  <xsl:text>function</xsl:text>
</xsl:template>

<xsl:template mode="process-mark" match="constructor">
  <xsl:text>function</xsl:text>
</xsl:template>

<xsl:template mode="process-mark" match="destructor">
  <xsl:text>function</xsl:text>
</xsl:template>

<xsl:template mode="process-mark" match="class">
  <xsl:text>struct</xsl:text>
</xsl:template>

<xsl:template mode="process-mark" match="enum">
  <xsl:text>enum</xsl:text>
</xsl:template>

<xsl:template mode="process-mark" match="typedef">
  <xsl:text>typedef</xsl:text>
</xsl:template>

<!--=====================================================================-->
<!-- process-children -->
<xsl:template mode="process-children" match="class|enum">
  <xsl:param name="parent-name" select="''"/>
  <xsl:param name="parent-link" select="''"/>

  <xsl:if test="child::*">
    <xsl:apply-templates select="child::*">
      <xsl:with-param name="parent-name" select="$parent-name"/>
      <xsl:with-param name="parent-link" select="$parent-link"/>
    </xsl:apply-templates>
  </xsl:if>
</xsl:template>


<xsl:template mode="process-children" match="typedef">
  <xsl:param name="parent-name" select="''"/>
  <xsl:param name="parent-link" select="''"/>

  <xsl:variable name="alias" select="@alias"/>
  <xsl:variable name="target" select="(/index/class[@name = $alias] |
                                       /index/enum[@name = $alias])[1]"/>

  <xsl:variable name="target-link">
    <xsl:apply-templates mode="process-link" select="$target"/>
  </xsl:variable>

  <xsl:if test="$alias and $target and $target/*">
    <xsl:apply-templates select="$target/*">
      <xsl:with-param name="parent-name" select="$parent-name"/>
      <xsl:with-param name="parent-link" select="$target-link"/>
    </xsl:apply-templates>
  </xsl:if>
</xsl:template>

<!--=====================================================================-->
<!-- INHERITANCE -->
<xsl:template match="inherits[1]">
  <xsl:param name="parent-name" select="''"/>
  <xsl:variable name="alias" select="@name"/>

  <xsl:call-template name="inherits-worker">
    <xsl:with-param name="pending" select="../inherits"/>
    <xsl:with-param name="parent-name" select="$parent-name"/>
  </xsl:call-template>
</xsl:template>

<xsl:template name="inherits-worker">
  <xsl:param name="finished" select="/.."/>
  <xsl:param name="pending" select="/.."/>
  <xsl:param name="parent-name" select="''"/>
  
  <xsl:if test="$pending">
    <!-- select an element to process and update pending and finished lists-->
    <xsl:variable name="current" select="$pending[1]"/>
    <xsl:variable name="pending2" select="$pending[position() > 1]"/>
    <xsl:variable name="finished2" select="$finished | $current"/>
    
    <!-- find the actual source class/enum -->
    <xsl:variable name="source" select="(/index/class[@name = $current/@name] |
                                         /index/enum[@name = $current/@name])[1]"/>
     
    <!-- check if current is not already processed and source is valid-->
    <xsl:if test="$source and not ($current[@name = $finished/@name])">
        
      <xsl:variable name="parent-link">
        <xsl:value-of select="$source/@link"/>
      </xsl:variable>
    
      <!-- import source contents -->
      <xsl:apply-templates select="$source/*[name() != 'constructor' and
                                             name() != 'destructor' and
                                             name() != 'inherits']">
        <xsl:with-param name="parent-name" select="$parent-name"/>
        <xsl:with-param name="parent-link" select="$parent-link"/>
      </xsl:apply-templates>
    </xsl:if>
    
    <!-- add unprocessed  'inherits' nodes from source -->
    <xsl:variable name="pending-add" select="$source/inherits[not (@name = $finished/@name)]"/>
    <xsl:variable name="pending3" select="$pending2 | $pending-add"/>
    
    <!-- process next node -->
    <xsl:call-template name="inherits-worker">
      <xsl:with-param name="finished" select="$finished2"/>
      <xsl:with-param name="pending" select="$pending3"/>
      <xsl:with-param name="parent-name" select="$parent-name"/>
    </xsl:call-template>
  </xsl:if>

</xsl:template>

<!--=====================================================================-->
<!-- HELPER FUNCTIONS -->
<!--
  Returns the last item of a tokenized string
-->
<xsl:template name="get-last-item">
  <xsl:param name="string" select="''"/>
  <xsl:param name="sep" select="'::'"/>
  <xsl:variable name="rest" select="substring-after($string, $sep)" />
  <xsl:choose>
    <xsl:when test="$rest">
      <xsl:call-template name="get-last-item">
        <xsl:with-param name="string" select="$rest" />
        <xsl:with-param name="sep" select="$sep" />
      </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="$string"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template name="output-identifier">
  <xsl:param name="name"/>
  <xsl:param name="link"/>
  <xsl:param name="mark"/>

  <keyword type="{$mark}" name="{$name}" link="{$link}"/>
</xsl:template>

</xsl:stylesheet>


