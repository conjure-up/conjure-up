#
# Makefile for conjure
#
NAME = conjure-up
CURRENT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
TOPDIR := $(shell basename `pwd`)
GIT_REV := $(shell git log --oneline -n1| cut -d" " -f1)
VERSION := 2.1.0


.PHONY: install-dependencies
install-dependencies:
	sudo apt-get -yy install devscripts equivs pandoc bsdtar jq libsystemd-dev tox snapcraft
	sudo mk-build-deps -i -t "apt-get --no-install-recommends -y" debian/control

.PHONY: uninstall-dependencies
uninstall-dependencies:
	sudo apt-get remove conjure-build-deps

release: update-version clean test

update-version:
	@sed -i -r "s/(^__version__\s=\s)(.*)/\1\"$(VERSION)\"/" conjureup/__init__.py
	@sed -i -r "1 s/(^conjure-up\s)\(([a-zA-Z0-9\.~\-\+]+)\)/\1\($(VERSION)\)/g" debian/changelog
	@sed -i -r "s/(^version:\s)(.*)/\1$(VERSION)/" snap/snapcraft.yaml

release-snap: update-version clean clean-snapcraft test
	@(cd snap && snapcraft)
	@echo
	@echo "Build complete, now run snapcraft push snap/$(NAME)_$(VERSION)_amd64.snap --release edge"
	@echo

clean:
	@-debian/rules clean
	@rm -rf *egg*
	@rm -rf site.py
	@rm -rf easy-install*
	@rm -rf docs/_build/*
	@rm -rf mockcfgpath
	@rm -rf ../conjure-up_*.deb ../cloud-*.deb ../conjure-up_*.tar.gz ../conjure-up_*.dsc ../conjure-up_*.changes \
		../conjure-up_*.build ../conjure-up-*.deb ../conjure-up_*.upload
	@rm -rf cover
	@rm -rf .coverage
	@rm -rf .tox
	@rm -rf conjure-up
	@rm -rf dist
	@rm -rf conjure-dev

clean-snapcraft:
	@(cd snap && snapcraft clean)

.PHONY: test
test:
	@tox -e py35,flake,isort

DPKGBUILDARGS = -us -uc -i'.git.*|.tox|.bzr.*|.editorconfig|.travis-yaml|macumba\/debian|' -i'snapcraft'
deb-src: clean
	@debuild -S -sa $(DPKGBUILDARGS)

deb-release:
	@debuild -S -sd $(DPKGBUILDARGS)

deb: clean
	@debuild -b $(DPKGBUILDARGS)

git-sync-requirements:
	if [ ! -f tools/sync-repo.py ]; then echo "Need to download sync-repo.py from https://git.io/v2mEw" && exit 1; fi
	tools/sync-repo.py -m repo-manifest.json -f

git_rev:
	@echo $(GIT_REV)

dev: clean
	tox -e conjure-dev
	@echo "Run 'source conjure-dev/bin/activate' to enter the dev venv"

# Indirection to allow 'make run' to build deb automatically, but
# 'make sbuild; make run' will not invoke 'deb'.
../conjure*.deb: deb
	echo "rule to make .deb automatically"

.PHONY: install
install: ../conjure*.deb
	sudo dpkg -i ../conjure-up_*deb
	sudo apt-get -yy install -f

# Fix some of the python formatting preferred by pylint
auto-format:
	@tox -e py35 -- isort -rc -m 3 conjureup test tools
	@tox -e py35 -- autopep8 --in-place --recursive conjureup test tools


all: release
