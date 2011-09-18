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
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

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
    <xsl:template match="//div[@class='noprint']"/>
    <xsl:template match="//div[@id='footer']"/>
    <!-- remove external links to unused resources -->
    <xsl:template match="/html/head/link[@rel = 'alternate']"/>
    <xsl:template match="/html/head/link[@rel = 'search']"/>
    <xsl:template match="/html/head/link[@rel = 'edit']"/>
    <xsl:template match="/html/head/link[@rel = 'stylesheet' and contains(@href,'http://en.cppreference.com')]"/>
    <xsl:template match="/html/head/link[@rel = 'stylesheet' and contains(@href,'http://en.cppreference.com/mwiki/index.php?title=-&amp;')]"/>
    <xsl:template match="/html/head/script[contains(@src,'http://en.cppreference.com/mwiki/index.php?title=-&amp;')]"/>
    <xsl:template match="/html/head/style[@type = 'text/css' and contains(text(),'http://en.cppreference.com/mwiki/index.php?title=MediaWiki:Geshi.css')]"/>

</xsl:stylesheet>
