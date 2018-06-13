#
# Makefile for conjure
#
NAME = conjure-up
CURRENT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
TOPDIR := $(shell basename `pwd`)
GIT_REV := $(shell git log --oneline -n1| cut -d" " -f1)
VERSION := $(shell cat VERSION)
CHANNEL := edge
PY36 := $(shell apt-cache search --names-only '^python3.6')

.PHONY: sysdeps
sysdeps:
	@if [ -z "$(PY36)" ]; then \
	    sudo add-apt-repository ppa:jonathonf/python-3.6; \
	fi
	@sudo apt-get update
	@sudo apt-get -qqyf install jq bsdtar bridge-utils software-properties-common snapcraft python3.6-dev tox shellcheck build-essential

travis-sysdeps:
	@sudo add-apt-repository -y ppa:jonathonf/python-3.6
	@sudo add-apt-repository -y ppa:adam-stokes/trusty-backports
	@sudo apt-get update -q
	@sudo apt-get remove -qy lxd lxd-client
	@sudo apt-get -y install jq bsdtar python3.6-dev make snapd libsodium-dev
	@sudo pip install tox
	@sudo snap install juju --classic
	@sudo snap refresh lxd
	@sudo snap install juju-wait --classic

.PHONY: install
install: snap
	@sudo snap install $(NAME)_$(VERSION)_amd64.snap --classic --dangerous

release: update-version clean test snap
	@snapcraft push $(NAME)_$(VERSION)_amd64.snap --release $(CHANNEL)

gen-changelog:
	if [ ! -f `which github_changelog_generator` ]; then echo "Need to install changelog generator: gem install github_changelog_generator, also generate a token https://git.io/vS1eF" && exit 1; fi
	@github_changelog_generator

update-version:
	@tools/update-version

snap: sysdeps update-version clean test
	@snapcraft
	@echo
	@echo "Build complete, now run snapcraft push $(NAME)_$(VERSION)_amd64.snap --release $(CHANNEL)"
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
	@find . -name \*.pyc -delete
	@find . -name __pycache__ -delete
	@rm -rf *.snap
	@rm -rf build

.PHONY: test
test: auto-format
	@tox -e py35,flake
	@shellcheck snap/wrappers/*

git_rev:
	@echo $(GIT_REV)

dev: clean
	tox -e conjure-dev
	@echo "Run 'source conjure-dev/bin/activate' to enter the dev venv"

# Fix some of the python formatting preferred by pylint
auto-format:
	@tox -e isort -- isort -rc -m 3 conjureup test tools
	@tox -e isort -- autopep8 --in-place --recursive conjureup test tools


all: release
