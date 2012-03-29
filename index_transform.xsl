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
<!--
  This is a base XSLT stylesheet for various transformations of the index.
  
  Each transformation should import this stylesheet, override the customization 
  hooks to specify the structure of the resulting document and call 
  <xsl:apply-templates mode="process-item"> for all direct children of the 
  <index> element in the function index. E.g.
  
  <xsl:template match="/index">
    <xsl:apply-templates mode="process-item" select="child::*"/>
  </xsl:template>
  
    USEFUL CUSTOMIZATION HOOKS
    
  name="output-item"
  
    Parameters
      "name" - full name of teh feature
      "link" - full link to the page of the feature relative to the wiki root
  
    Called to output the information about the feature to the resulting document.
    By default does nothing. Override in order to output content.
  
  name="inherits-worker"
    
    Processes the inheritance tree. Override with an empty template to disable
    the processing of inherited identifiers.
    
  name="process-item-finalize"
  
    Parameters
      "name" - full name of the feature
      "link" - full link to the page of the feature relative to the wiki root
        
    Called to output information of a feature and continue the processing of the
    children. By default just calls "output-item" and "process-children" with 
    appropriate parameters.
    
    Exists in order to allow to wrap entire contents of an element (children 
    included) with arbitrary elements. Useful only when the transformed index 
    needs to be hierarchical. If there's no such requirement, look at 
    "output-item".
    
-->
  
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                >

<!--
  Main processing template
  
  Processes one entry. Calls various other templates to pull required information.
  Then calls "process-item-finalize"
-->
<xsl:template mode="process-item" match="const|function|class|enum|typedef|constructor|destructor|specialization|overload">

  <xsl:param name="parent-name" select="''"/>
  <xsl:param name="parent-link" select="''"/>

  <xsl:variable name="name">
    <xsl:apply-templates mode="get-name" select="."/>
  </xsl:variable>

  <xsl:variable name="link">
    <xsl:apply-templates mode="get-link" select="."/>
  </xsl:variable>

  <xsl:variable name="full-name">
    <xsl:apply-templates mode="get-full-name" select=".">
      <xsl:with-param name="name" select="$name"/>
      <xsl:with-param name="parent-name" select="$parent-name"/>
    </xsl:apply-templates>
  </xsl:variable>

  <xsl:variable name="full-link">
    <xsl:apply-templates mode="get-full-link" select=".">
      <xsl:with-param name="link" select="$link"/>
      <xsl:with-param name="parent-link" select="$parent-link"/>
    </xsl:apply-templates>
  </xsl:variable>

  <xsl:call-template name="process-item-finalize">
    <xsl:with-param name="name" select="$full-name"/>
    <xsl:with-param name="link" select="$full-link"/>
  </xsl:call-template>
</xsl:template>

<!--
  Wrapper around "inherits-worker" which builds the initial list of base classes
  to process
-->
<xsl:template mode="process-item" match="inherits[1]">
  <xsl:param name="parent-name" select="''"/>
  <xsl:variable name="alias" select="@name"/>

  <xsl:call-template name="inherits-worker">
    <xsl:with-param name="pending" select="../inherits"/>
    <xsl:with-param name="parent-name" select="$parent-name"/>
  </xsl:call-template>
</xsl:template>

<!-- 
  Adds the members of the base classes. Calls itself recursively to process each
  base class. A list of already processed classes is maintained and passed as
  a parameter in order to avoid duplications if daemond inheritance is present.
-->
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
      <xsl:apply-templates mode="process-item" 
                           select="$source/*[name() != 'constructor' and
                                             name() != 'destructor' and
                                             name() != 'inherits' and
                                             name() != 'specialization' and
                                             name() != 'overload']">
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
<!-- process-children 

  Calls "process-item" templates for each child if the node can contain children
-->
<xsl:template mode="process-children" match="class|enum">
  <xsl:param name="parent-name" select="''"/>
  <xsl:param name="parent-link" select="''"/>

  <xsl:if test="child::*">
    <xsl:apply-templates mode="process-item" select="child::*">
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
    <xsl:apply-templates mode="get-link" select="$target"/>
  </xsl:variable>

  <xsl:if test="$alias and $target and $target/*">
    <xsl:apply-templates mode="process-item" select="$target/*">
      <xsl:with-param name="parent-name" select="$parent-name"/>
      <xsl:with-param name="parent-link" select="$target-link"/>
    </xsl:apply-templates>
  </xsl:if>
</xsl:template>

<!--=====================================================================-->
<!-- get-name 

  Results in name of the feature, relative to the parent class, or the global
  namespace if there's no such class.
-->
<xsl:template mode="get-name" match="*">
  <xsl:value-of select="@name"/>
</xsl:template>

<!--=====================================================================-->
<!-- get-link 

  Results in link to the relevant page, relative to the parent class, or the 
  wiki root if there's no such class
-->
<xsl:template mode="get-link" match="*">
  <xsl:choose>
    <xsl:when test="@link='.'"/>
    <xsl:when test="@link"><xsl:value-of select="@link"/></xsl:when>
    <xsl:otherwise><xsl:value-of select="@name"/></xsl:otherwise>
  </xsl:choose>
</xsl:template>

<!--=====================================================================-->
<!-- get-full-name 

  Results in full name of the feature (i.e. including the name of the parent 
  class, if any).
-->
<xsl:template mode="get-full-name" match="*">
  <xsl:param name="name" select="''"/>
  <xsl:param name="parent-name" select="''"/>

  <xsl:value-of select="$parent-name"/>
  <xsl:if test="$parent-name"><xsl:text>::</xsl:text></xsl:if>
  <xsl:value-of select="$name"/>
</xsl:template>


<xsl:template mode="get-full-name" match="constructor">
  <xsl:param name="parent-name" select="''"/>

  <xsl:value-of select="$parent-name"/>
  <xsl:if test="$parent-name"><xsl:text>::</xsl:text></xsl:if>

  <xsl:call-template name="get-last-item">
    <xsl:with-param name="string" select="$parent-name"/>
    <xsl:with-param name="sep" select="'::'"/>
  </xsl:call-template>
</xsl:template>


<xsl:template mode="get-full-name" match="destructor">
  <xsl:param name="parent-name" select="''"/>

  <xsl:value-of select="$parent-name"/>
  <xsl:if test="$parent-name"><xsl:text>::</xsl:text></xsl:if>
  <xsl:text>~</xsl:text>

  <xsl:call-template name="get-last-item">
    <xsl:with-param name="string" select="$parent-name"/>
    <xsl:with-param name="sep" select="'::'"/>
  </xsl:call-template>
</xsl:template>


<xsl:template mode="get-full-name" match="overload">
  <xsl:param name="name" select="''"/>
  <xsl:param name="parent-name" select="''"/>

  <xsl:value-of select="$name"/>
  <xsl:text>(</xsl:text>
  <xsl:value-of select="$parent-name"/>
  <xsl:text>)</xsl:text>
</xsl:template>


<xsl:template mode="get-full-name" match="specialization">
  <xsl:param name="name" select="''"/>
  <xsl:param name="parent-name" select="''"/>

  <xsl:value-of select="$name"/>
  <xsl:text>&lt;</xsl:text>
  <xsl:value-of select="$parent-name"/>
  <xsl:text>&gt;</xsl:text>
</xsl:template>

<!--=====================================================================-->
<!-- get-full-link 

  Results in full link (i.e. relative to the wiki root) to the relevant page 
  describing the feature
-->
<xsl:template mode="get-full-link" match="*">
  <xsl:param name="link" select="''"/>
  <xsl:param name="parent-link" select="''"/>

  <xsl:value-of select="$parent-link"/>
    <xsl:if test="string($parent-link) and string($link)"><xsl:text>/</xsl:text></xsl:if>
  <xsl:value-of select="$link"/>
</xsl:template>


<xsl:template mode="get-full-link" match="typedef">
  <xsl:param name="link" select="''"/>
  <xsl:param name="parent-link" select="''"/>

  <xsl:variable name="alias" select="@alias"/>
  <xsl:variable name="target" select="(/index/class[@name = $alias] |
                                       /index/enum[@name = $alias])[1]"/>

  <xsl:variable name="target-link">
    <xsl:apply-templates mode="get-link" select="$target"/>
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


<xsl:template mode="get-full-link" match="constructor">
  <xsl:param name="parent-link" select="''"/>

  <xsl:value-of select="$parent-link"/>
  <xsl:if test="string($parent-link)"><xsl:text>/</xsl:text></xsl:if>

  <xsl:call-template name="get-last-item">
    <xsl:with-param name="string" select="$parent-link"/>
    <xsl:with-param name="sep" select="'/'"/>
  </xsl:call-template>
</xsl:template>


<xsl:template mode="get-full-link" match="destructor">
  <xsl:param name="parent-link" select="''"/>

  <xsl:value-of select="$parent-link"/>
  <xsl:if test="string($parent-link)"><xsl:text>/</xsl:text></xsl:if>

  <xsl:call-template name="get-last-item">
    <xsl:with-param name="string" select="$parent-link"/>
    <xsl:with-param name="sep" select="'/'"/>
  </xsl:call-template>
</xsl:template>

<!--=====================================================================-->
<!-- HELPER FUNCTIONS -->
<!--
  Returns the last token of a string.
  
  Parameters:
    "string" - string to tokenize
    "sep" - separator
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

<!--=====================================================================-->
<!-- DEFAULT IMPLEMENTATIONS -->

<xsl:template name="process-item-finalize">
  <xsl:param name="name"/>
  <xsl:param name="link"/>

  <xsl:call-template name="output-item">
    <xsl:with-param name="name" select="$name"/>
    <xsl:with-param name="link" select="$link"/>
  </xsl:call-template>

  <xsl:apply-templates mode="process-children" select=".">
    <xsl:with-param name="parent-name" select="$name"/>
    <xsl:with-param name="parent-link" select="$link"/>
  </xsl:apply-templates>
</xsl:template>
  
<xsl:template name="output-item">
  <xsl:param name="name"/>
  <xsl:param name="link"/>
</xsl:template>

</xsl:stylesheet>


