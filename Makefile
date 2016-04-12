#
# Makefile for conjure
#
NAME = conjure
TOPDIR := $(shell basename `pwd`)
GIT_REV := $(shell git log --oneline -n1| cut -d" " -f1)
VERSION := $(shell ./tools/version)

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
	@rm -rf dist

DPKGBUILDARGS = -us -uc -i'.git.*|.tox|.bzr.*|.editorconfig|.travis-yaml|macumba\/debian|maasclient\/debian'
deb-src: clean update_version
	@debuild -S -sa $(DPKGBUILDARGS)

deb-release:
	@debuild -S -sd $(DPKGBUILDARGS)

deb: clean update_version
	@debuild -b $(DPKGBUILDARGS)

current_version:
	@echo $(VERSION)

git-sync-requirements:
	if [ ! -f tools/sync-repo.py ]; then echo "Need to download sync-repo.py from https://git.io/v2mEw" && exit 1; fi
	tools/sync-repo.py -m repo-manifest.json -f

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
