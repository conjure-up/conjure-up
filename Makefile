#
# Makefile for conjure
#
NAME = conjure-up
CURRENT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
TOPDIR := $(shell basename `pwd`)
GIT_REV := $(shell git log --oneline -n1| cut -d" " -f1)
VERSION := 2.2-beta3


.PHONY: sysdeps
sysdeps:
	@sudo apt-get update
	@sudo apt-get -qqyf install jq python3-yaml bsdtar bridge-utils software-properties-common snapcraft

.PHONY: install
install: snap
	@sudo snap install $(NAME)_$(VERSION)_amd64.snap --classic --dangerous

release: update-version clean test snap
	@snapcraft push $(NAME)_$(VERSION)_amd64.snap --release edge

update-version:
	@sed -i -r "s/(^__version__\s=\s)(.*)/\1\"$(VERSION)\"/" conjureup/__init__.py
	@sed -i -r "s/(^version:\s)(.*)/\1$(VERSION)/" snap/snapcraft.yaml

snap: sysdeps update-version clean test
	@snapcraft
	@echo
	@echo "Build complete, now run snapcraft push $(NAME)_$(VERSION)_amd64.snap --release edge"
	@echo "Or install with sudo snap install $(NAME)_$(VERSION)_amd64.snap --classic --dangerous"
	@echo

clean:
	@snapcraft clean
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
	@find bundleplacer/ -name \*.pyc -delete
	@find conjureup/ -name \*.pyc -delete
	@find test/ -name \*.pyc -delete
	@find ubuntui/ -name \*.pyc -delete
	@find macumba/ -name \*.pyc -delete
	@find . -name __pycache__ -delete

.PHONY: test
test: auto-format
	@tox -e py35,flake,isort

git-sync-requirements:
	if [ ! -f tools/sync-repo.py ]; then echo "Need to download sync-repo.py from https://git.io/v2mEw" && exit 1; fi
	tools/sync-repo.py -m repo-manifest.json -f

git_rev:
	@echo $(GIT_REV)

dev: clean
	tox -e conjure-dev
	@echo "Run 'source conjure-dev/bin/activate' to enter the dev venv"

# Fix some of the python formatting preferred by pylint
auto-format:
	@tox -e py35 -- isort -rc -m 3 conjureup test tools
	@tox -e py35 -- autopep8 --in-place --recursive conjureup test tools


all: release
