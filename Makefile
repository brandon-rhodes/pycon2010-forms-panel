# Makefile

PYTHON := /usr/bin/python

all: presentation.html

presentation.html: presentation.rst bin/wrap_slides.py
	rst2s5.py $< > $@
	bin/wrap_slides.py $@
