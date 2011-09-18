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
