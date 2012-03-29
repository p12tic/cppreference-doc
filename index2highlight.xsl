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
<xsl:output indent="no" method="text"/>

<xsl:template match="/index">
  <xsl:apply-templates mode="process-item" select="child::*"/>
</xsl:template>

<xsl:template name="output-item">
  <xsl:param name="name"/>
  <xsl:param name="link"/>
  
  <xsl:if test="(not (name(..) != 'index' and (name() = 'function' or 
                                               name() = 'constructor' or
                                               name() = 'destructor'))
                ) and (not (contains($name, '&lt;') or 
                            contains($name, '&gt;') or
                            contains($name, '(') or
                            contains($name, ')')))">
    <xsl:value-of select="$name"/><xsl:text> => </xsl:text><xsl:value-of select="$link"/><xsl:text>
</xsl:text>
  </xsl:if>
</xsl:template>

<xsl:template name="inherits-worker"/>
</xsl:stylesheet>


