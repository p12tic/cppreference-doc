<?xml version="1.0" encoding="UTF-8"?>
<!--
    Copyright (C) 2011  Povilas Kanapickas <povilas@radix.lt>

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
<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:str="http://exslt.org/strings">

  <xsl:output
    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
    omit-xml-declaration="yes"
  />

  <xsl:template match="node()|@*">
    <xsl:copy>
      <xsl:apply-templates select="node()|@*"/>
    </xsl:copy>
  </xsl:template>

  <!-- remove useless UI elements-->
  <xsl:template match="//*[contains(@class, 'noprint ')]"/>
  <xsl:template match="//*[contains(@class, ' noprint')]"/>
  <xsl:template match="//*[@class='noprint']"/>

  <!-- remove 'See also' links between C and C++ parts of the documentation -->
  <xsl:template match="
    //tr[
      @class = 't-dcl-list-item'
      and .//td/div[
        @class = 't-dcl-list-see'
      ]
    ]"/>

  <xsl:template match="
    //tr[
      ./td[
        @class = 't-dcl-list-sep'
      ]
      and following-sibling::tr[1][
        @class = 't-dcl-list-item'
        and .//td/div[
          @class = 't-dcl-list-see'
        ]
      ]
    ]"/>

  <xsl:template match="
    //h3[
      .//span[
        @id = 'See_also'
      ]
      and following-sibling::table[1][
        @class = 't-dcl-list-begin'
        and (count(./tr) = 2 or count(./tbody/tr) = 2)
        and .//td/div [
          @class = 't-dcl-list-see'
        ]
      ]
    ]"/>

  <!-- remove external links to unused resources -->
  <xsl:template match="/html/head/link[@rel = 'alternate']"/>
  <xsl:template match="/html/head/link[@rel = 'search']"/>
  <xsl:template match="/html/head/link[@rel = 'edit']"/>
  <xsl:template match="/html/head/link[@rel = 'EditURI']"/>

  <!-- remove Google Analytics scripts -->
  <xsl:template match="/html/body/script[contains(text(),'google-analytics.com/ga.js')]"/>
  <xsl:template match="/html/body/script[contains(@src, 'google-analytics.com/ga.js')]"/>
  <xsl:template match="/html/body/script[contains(text(),'pageTracker')]"/>

</xsl:stylesheet>
