#   Copyright (C) 2011, 2012  p12 <tir5c3@yahoo.co.uk>
#
#   This file is part of cppreference-doc
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see http://www.gnu.org/licenses/.

SHELL := /bin/bash

#Common prefixes

prefix = /usr
datarootdir = $(prefix)/share
docdir = $(datarootdir)/cppreference/doc
bookdir = $(datarootdir)/devhelp/books

#Version

VERSION=20120620

#STANDARD RULES

all: doc_devhelp doc_qch

DISTFILES=	\
		reference/				\
		images/					\
		build_link_map.py		\
		devhelp2qch.xsl			\
		fix_devhelp-links.xsl	\
		httrack-workarounds.py	\
		index2browser.xsl		\
		index2devhelp.xsl		\
		index2search.xsl		\
		index2highlight.xsl		\
		index_transform.xsl		\
		index-chapters-c.xml	\
		index-chapters-cpp.xml	\
		index-functions.README	\
		index-functions-c.xml	\
		index-functions-cpp.xml	\
		preprocess.py			\
		preprocess.xsl			\
		preprocess-css.css		\
		Makefile				\
		README

CLEANFILES= \
		output								\
		images/output						\
		cppreference-doc-en-c.devhelp2		\
		cppreference-doc-en-cpp.devhelp2	\
		cppreference-doc-en-c.qch			\
		cppreference-doc-en-cpp.qch			\
		qch-help-project-cpp.xml			\
		qch-files.xml						\
		devhelp-index-c.xml					\
		devhelp-index-cpp.xml				\
		link-map.xml

clean:
	rm -rf $(CLEANFILES)

check:

dist: clean
	mkdir -p "cppreference-doc-$(VERSION)"
	cp -r $(DISTFILES) "cppreference-doc-$(VERSION)"
	tar czf "cppreference-doc-$(VERSION).tar.gz" "cppreference-doc-$(VERSION)"
	rm -rf "cppreference-doc-$(VERSION)"

install:
	# install the devhelp documentation
	pushd "output" > /dev/null; \
	find . -type f \
		-exec install -DT -m 644 '{}' "$(DESTDIR)$(docdir)/html/{}" \; ; \
	popd > /dev/null

	install -DT -m 644 cppreference-doc-en-c.devhelp2 \
		"$(DESTDIR)$(bookdir)/cppreference-doc-en-c/cppreference-doc-en-c.devhelp2"
	install -DT -m 644 cppreference-doc-en-cpp.devhelp2 \
		"$(DESTDIR)$(bookdir)/cppreference-doc-en-cpp/cppreference-doc-en-cpp.devhelp2"

	# install the .qch (Qt Help) documentation
	install -DT -m 644 cppreference-doc-en-cpp.qch $(DESTDIR)$(docdir)/qch/cppreference-doc-en-cpp.qch

uninstall:
	rm -rf "$(DESTDIR)$(docdir)"
	rm -rf "$(DESTDIR)$(bookdir)"

#WORKER RULES

doc_devhelp: cppreference-doc-en-c.devhelp2 cppreference-doc-en-cpp.devhelp2

doc_qch: cppreference-doc-en-cpp.qch

#builds the title<->location map
link-map.xml: output
	./build_link_map.py

#build the .devhelp2 index
cppreference-doc-en-c.devhelp2: output link-map.xml
	xsltproc --stringparam book-base $(docdir)/html 			\
			 --stringparam chapters-file index-chapters-c.xml	\
			 --stringparam title "C Standard Library reference"	\
			 --stringparam name "cppreference-doc-en-c"	\
			 index2devhelp.xsl index-functions-c.xml > devhelp-index-c.xml
	xsltproc fix_devhelp-links.xsl devhelp-index-c.xml > cppreference-doc-en-c.devhelp2

cppreference-doc-en-cpp.devhelp2: output link-map.xml
	xsltproc --stringparam book-base $(docdir)/html 			\
			 --stringparam chapters-file index-chapters-cpp.xml	\
			 --stringparam title "C++ Standard Library reference"	\
			 --stringparam name "cppreference-doc-en-cpp"	\
			 index2devhelp.xsl index-functions-cpp.xml > devhelp-index-cpp.xml
	xsltproc fix_devhelp-links.xsl devhelp-index-cpp.xml > cppreference-doc-en-cpp.devhelp2

#build the .qch (QT help) file
cppreference-doc-en-cpp.qch: qch-help-project-cpp.xml
	#qhelpgenerator only works if the project file is in the same directory as the documentation
	cp qch-help-project-cpp.xml output/qch.xml

	pushd "output" > /dev/null; \
	qhelpgenerator qch.xml -o "../cppreference-doc-en-cpp.qch"; \
	popd > /dev/null

	rm -f output/qch.xml

qch-help-project-cpp.xml: cppreference-doc-en-cpp.devhelp2
	#build the file list
	echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?><files>" > "qch-files.xml"

	pushd "output" > /dev/null; \
	find . -type f -not -iname "*.ttf" \
		-exec echo "<file>"'{}'"</file>" >> "../qch-files.xml" \; ; \
	popd > /dev/null

	echo "</files>" >> "qch-files.xml"

	#create the project (copies the file list)
	xsltproc devhelp2qch.xsl cppreference-doc-en-cpp.devhelp2 > "qch-help-project-cpp.xml"

#create preprocessed archive
output:
	./preprocess.py

#redownloads the source documentation directly from en.cppreference.com
source:
	rm -rf "reference"
	mkdir "reference"

	pushd "reference" > /dev/null; \
	httrack http://en.cppreference.com/w/ -k --near --include-query-string \
	  -* +en.cppreference.com/* +upload.cppreference.com/* -*index.php\?* \
	  -*/Special:* -*/Talk:* -*/Help:* -*/File:* -*/Cppreference:* -*/WhatLinksHere:* \
	  -*/Template:* -*/Category:* -*action=* -*printable=* \
	  +*MediaWiki:Common.css* +*MediaWiki:Print.css* +*MediaWiki:Vector.css* \
	  -*MediaWiki:Geshi.css* "+*title=-&action=raw*" --timeout=180 --retries=10 ;\
	popd > /dev/null

	#delete useless files
	rm -rf "reference/hts-cache"
	rm -f "reference/backblue.gif"
	rm -f "reference/fade.gif"
	rm -f "reference/hts-log.txt"
	rm -f "reference/index.html"

	#download files that httrack has forgotten
	./httrack-workarounds.py

