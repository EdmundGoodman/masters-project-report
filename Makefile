# requires GNU make
SHELL=/bin/bash

LATEX_EXTRA_FLAGS ?= -shell-escape -synctex=1

.DELETE_ON_ERROR:

%.pdf %.aux %.idx: %.tex
	pdflatex -halt-on-error -file-line-error ${LATEX_EXTRA_FLAGS} $<
	while grep 'Rerun to get ' $*.log ; do pdflatex -halt-on-error ${LATEX_EXTRA_FLAGS} $< ; done
%.ind: %.idx
	makeindex $*
%.bbl: %.aux
	bibtex $*
%.pdftex %.pdftex_t: %.fig
	fig2dev -L pdftex_t -p $*.pdftex $< $*.pdftex_t
	fig2dev -L pdftex $< $*.pdftex

all: report.pdf report-submission.pdf

report-submission.tex: report.tex
	sed -e 's/^%\(\\submissiontrue\)/\1/' $< >$@

report.pdf: images/logo-dcst-colour.pdf

# extract number of first and last page of the main chapters from the AUX file
WORDCOUNT_FILE=report-submission
# FIRSTPAGE?=$(shell sed -ne 's/^\\newlabel{firstcontentpage}{{[0-9\.]*}{\([0-9]*\)}.*/\1/p' $(WORDCOUNT_FILE).aux)
# LASTPAGE ?=$(shell sed -ne 's/^\\newlabel{lastcontentpage}{{[0-9\.]*}{\([0-9]*\)}.*/\1/p' $(WORDCOUNT_FILE).aux)
FIRSTPAGE?=$(shell sed -ne 's/.*\\zref@newlabel{firstpdfcontentpage}{.*\\abspage{\([0-9]*\)}}.*/\1/p' $(WORDCOUNT_FILE).aux)
AFTERLASTPAGE:=$(shell sed -ne 's/.*\\zref@newlabel{lastpdfcontentpage}{.*\\abspage{\([0-9]*\)}}.*/\1/p' $(WORDCOUNT_FILE).aux)
LASTPAGE?=$(shell expr $(AFTERLASTPAGE) - 1)

# requires ghostscript
.PHONY: wordcount
wordcount: $(WORDCOUNT_FILE).pdf
	gs -q -dSAFER -sDEVICE=txtwrite -o - \
	   -dFirstPage=$(FIRSTPAGE) -dLastPage=$(LASTPAGE) $< | \
	egrep '[A-Za-z]{3}' | wc -w

.PHONY: texwordcount
texwordcount: report-submission.tex
	texcount -inc -total -sum -brief report-submission.tex
# texcount -inc -total report-submission.tex | grep -E "Words in text:|Words outside text" | awk -F: '{sum += $$2} END {print sum}'
# texcount -inc report-submission.tex | grep "Words in text:" | tail -n 1

.PHONY: lexers
lexers: tools/generate_lexers_json.py
	python3 tools/generate_lexers_json.py

.PHONY: clean
clean:
	rm -f *.log *.aux *.toc *.bbl *.ind *.lot *.lof *.out *.acn *.ist *.lol *~ *.bcf *.fdb_latexmk *.fls *.glo *.flsdefs *.pyg *.run.xml *.glsdefs *.synctex.gz *.bcf-SAVE-ERROR
	rm -rf _minted-report _minted-report-submission
	rm -f report-submission.tex

.PHONY: clobber
clobber: clean
	rm -f report.pdf report-submission.pdf
