FILE=jan-pisl-bp-2018

all:
	pdflatex $(FILE)
	bibtex $(FILE)

clean:
	rm -f *~ *.aux *.log *.out *.bbl *.blg *.loa *.lof *.bst *.bak\
	*.toc *.lot

distclean:
	make clean
	rm -f $(FILE).pdf
