#
# Makefile for conjure
#
NAME = conjure
TOPDIR := $(shell basename `pwd`)
GIT_REV := $(shell git log --oneline -n1| cut -d" " -f1)
VERSION := $(shell ./tools/version)
UPSTREAM_MACUMBA := https://github.com/Ubuntu-Solutions-Engineering/macumba.git
UPSTREAM_MACUMBA_COMMIT := v0.9.1
UPSTREAM_MAASCLIENT := https://github.com/Ubuntu-Solutions-Engineering/maasclient.git
UPSTREAM_MAASCLIENT_COMMIT := v0.3
UPSTREAM_UBUNTUI := https://github.com/Ubuntu-Solutions-Engineering/urwid-ubuntu.git
UPSTREAM_UBUNTUI_COMMIT := v0.1.1

.PHONY: install-dependencies
install-dependencies:
	sudo apt-get -yy install devscripts equivs pandoc
	sudo mk-build-deps -i -t "apt-get --no-install-recommends -y" debian/control

.PHONY: uninstall-dependencies
uninstall-dependencies:
	sudo apt-get remove conjure-build-deps

update_version: git-sync-requirements
	wrap-and-sort
	@sed -i -r "s/(^__version__\s=\s)(.*)/\1\"$(VERSION)\"/" conjure/__init__.py

clean:
	@-debian/rules clean
	@rm -rf docs/_build/*
	@rm -rf mockcfgpath
	@rm -rf ../conjure_*.deb ../cloud-*.deb ../conjure_*.tar.gz ../conjure_*.dsc ../conjure_*.changes \
		../conjure_*.build ../conjure-*.deb ../conjure_*.upload
	@rm -rf cover
	@rm -rf .coverage
	@rm -rf .tox

DPKGBUILDARGS = -us -uc -i'.git.*|.tox|.bzr.*|.editorconfig|.travis-yaml|macumba\/debian|maasclient\/debian'
deb-src: clean update_version
	@debuild -S -sa $(DPKGBUILDARGS)

deb-release:
	@debuild -S -sd $(DPKGBUILDARGS)

deb: clean update_version man-pages
	@debuild -b $(DPKGBUILDARGS)

man-pages:
	@pandoc -s docs/conjure-setup.md -t man -o man/en/conjure-setup.1

current_version:
	@echo $(VERSION)

git-sync-requirements:
	@echo Syncing git repos $(UPSTREAM_MACUMBA), $(UPSTREAM_MAASCLIENT), $(UPSTREAM_UBUNTUI)
	@rm -rf tmp && mkdir -p tmp
	@rm -rf macumba
	@rm -rf maasclient
	@rm -rf ubuntui
	@git clone -q $(UPSTREAM_MACUMBA) tmp/macumba
	@git clone -q $(UPSTREAM_MAASCLIENT) tmp/maasclient
	@git clone -q $(UPSTREAM_UBUNTUI) tmp/ubuntui
	@(cd tmp/maasclient && git checkout -q -f $(UPSTREAM_MAASCLIENT_COMMIT))
	@(cd tmp/macumba && git checkout -q -f $(UPSTREAM_MACUMBA_COMMIT))
	@(cd tmp/ubuntui && git checkout -q -f $(UPSTREAM_UBUNTUI_COMMIT))
	@rsync -C -az --delete tmp/macumba/macumba .
	@rsync -C -az --delete tmp/maasclient/maasclient .
	@rsync -C -az --delete tmp/ubuntui/ubuntui .
	@rm -rf tmp

git_rev:
	@echo $(GIT_REV)

pyflakes:
	pyflakes conjure test bin

pep8:
	pep8 conjure test bin

# Indirection to allow 'make run' to build deb automatically, but
# 'make sbuild; make run' will not invoke 'deb'.
../conjure*.deb: deb
	echo "rule to make .deb automatically"

.PHONY: install
install: ../conjure*.deb
	-dpkg -i ../conjure_*deb
	-dpkg -i ../conjure-${type}*deb
	apt-get -yy install -f

all: deb
