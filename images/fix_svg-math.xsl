<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
                xmlns="http://www.w3.org/2000/svg"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:str="http://exslt.org/strings"
                xmlns:svg="http://www.w3.org/2000/svg"
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

</xsl:stylesheet>
