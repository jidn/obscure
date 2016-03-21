# This helps with creating local virtual environments, requirements,
# syntax checking, running tests, coverage and uploading packages to PyPI.
# Homepage at https://github.com/jidn/python-Makefile
# 
# This also works with Travis CI
#
PROJECT :=
PACKAGE := obscure.py
# Replace 'requirements.txt' with another filename if needed.
REQUIREMENTS := $(wildcard requirements.txt)
# Directory with all the tests
TESTDIR := test
TESTREQUIREMENTS := $(wildcard $(TESTDIR)/requirements.txt)
##############################################################################
# Python settings
ifdef TRAVIS
	ENV = $(VIRTUAL_ENV)
else
	PYTHON_VERSION :=3.5
	ENV := env
endif

# System paths
BIN := $(ENV)/bin
OPEN := xdg-open
SYS_VIRTUALENV := virtualenv
SYS_PYTHON := python$(PYTHON_VERSION)

# virtualenv executables
PIP := $(BIN)/pip
PYTHON := $(BIN)/python
FLAKE8 := $(BIN)/flake8
PEP257 := $(BIN)/pep257
COVERAGE := $(BIN)/coverage
TESTRUN := $(BIN)/py.test

# Project settings
SETUP_PY := $(wildcard setup.py)
SOURCES := $(shell find $(PACKAGE) -name '*.py')
TESTS :=   $(shell find $(TESTDIR) -name '*.py')
EGG_INFO := $(subst -,_,$(PROJECT)).egg-info

# Flags for environment/tools
DEPENDS_CI := $(ENV)/.depends-ci
DEPENDS_DEV := $(ENV)/.depends-dev

# Main Targets ###############################################################
.PHONY: all env ci help
all: $(ENV)/.default-target
$(ENV)/.default-target: env Makefile $(SETUP_PY) $(SOURCES)
	$(MAKE) check
	@touch $@

# Target for Travis
ci: test

help:
	@echo "env        Create virtualenv and install requirements"
	@echo "check      Run style checks"
	@echo "test       Run tests"
	@echo "pdb        Run tests, but stop at the first unhandled exception."
	@echo "coverage   Get coverage information."
	@echo "upload     Upload package to PyPI."
	@echo "clean clean-all  Clean up and clean up removing virtualenv."

# Environment Installation ###################################################
env: $(PIP) $(ENV)/.requirements $(ENV)/.setup.py
$(PIP):
	$(SYS_VIRTUALENV) --python $(SYS_PYTHON) $(ENV)
	@$(MAKE) -s $(ENV)/.requirements
	@$(MAKE) -s $(ENV)/.setup.py

$(ENV)/.requirements: $(REQUIREMENTS)
ifneq ($(REQUIREMENTS),)
	$(PIP) install --upgrade -r $(REQUIREMENTS)
	# env requirements hook
	$(info Upgrade or install $(REQUIREMENTS) complete.)
endif
	@touch $@

$(ENV)/.setup.py: $(SETUP_PY)
ifneq ($(SETUP_PY),)
	$(PIP) install -e .
endif
	@touch $@

### Static Analysis & Travis CI ##############################################
.PHONY: check flake8 pep257

PEP8_IGNORED := E501,E123,D104,D203,D205
check: flake8 pep257

$(DEPENDS_CI): env $(TESTREQUIREMENTS)
	$(PIP) install --upgrade flake8 pep257
	touch $(DEPENDS_CI)  # flag to indicate dependencies are installed

$(DEPENDS_DEV): env
	$(PIP) install --upgrade wheel  # pygments wheel
	@touch $@  # flag to indicate dependencies are installed

flake8: $(DEPENDS_CI)
	$(FLAKE8) $(or $(PACKAGE), $(SOURCES)) $(TESTDIR) --ignore=$(PEP8_IGNORED)

pep257: $(DEPENDS_CI)
	$(PEP257) $(or $(PACKAGE), $(SOURCES)) $(TESTDIR) --ignore=$(PEP8_IGNORED)

### Testing ##################################################################
.PHONY: test pdb coverage

TESTRUN_OPTS := --cov $(PACKAGE) \
			   --cov-report term-missing \
			   --cov-report html 

test: .test-env
	$(TESTRUN) $(TESTDIR) $(TESTRUN_OPTS) 

pdb: .test-env
	$(TESTRUN) $(TESTDIR) -x --pdb

.test-env: env $(DEPENDS_CI) $(TESTS) $(TESTRUN) $(COVERAGE) $(ENV)/requirements-test $(TESTDIR)/doc_test.txt
	@touch $@

$(TESTDIR)/doc_test.txt: $(SOURCES)
	@sed '1,/^Example/d;/^"""/,$$d;s/^    //' obscure.py > $(TESTDIR)/doc_test.txt

$(TESTRUN):
	$(PIP) install --upgrade pytest
	@touch $@

$(ENV)/requirements-test: $(TESTREQUIREMENTS)
ifneq ($(TESTREQUIREMENTS),)
	$(PIP) install --upgrade -r $(TESTREQUIREMENTS)
	@echo "Testing requirements installed."
endif
	@touch $@

coverage: test $(COVERAGE)
	$(COVERAGE) html
	$(OPEN) htmlcov/index.html

$(COVERAGE):
	$(PIP) install coverage
	@touch $@

# Cleanup ####################################################################
.PHONY: clean clean-env clean-all .clean-build .clean-test .clean-dist

clean: .clean-dist .clean-test .clean-build
	@rm -rf $(ALL)

clean-env: clean
	@rm -rf $(ENV)

clean-all: clean clean-env

.clean-build:
#	@find -name $(PACKAGE).c -delete
	@find $(TESTDIR) -name '*.pyc' -delete
	@find $(TESTDIR) -name '__pycache__' -delete
	@rm -rf $(EGG_INFO)
	@rm -rf __pycache__

.clean-test:
	@rm -rf .coverage
#	@rm -f *.log

.clean-dist:
	@rm -rf dist build

# Release ####################################################################
# For more information on creating packages for PyPI see the writeup at
# http://peterdowns.com/posts/first-time-with-pypi.html
.PHONY: authors register dist upload .git-no-changes

authors:
	echo "Authors\n=======\n\nA huge thanks to all of our contributors:\n\n" > AUTHORS.md
	git log --raw | grep "^Author: " | cut -d ' ' -f2- | cut -d '<' -f1 | sed 's/^/- /' | sort | uniq >> AUTHORS.md

register: 
	$(PYTHON) setup.py register -r pypi

dist: test
	$(PYTHON) setup.py sdist
	$(PYTHON) setup.py bdist_wheel

upload: .git-no-changes register
	$(PYTHON) setup.py sdist upload -r pypi
	$(PYTHON) setup.py bdist_wheel upload -r pypi

.git-no-changes:
	@if git diff --name-only --exit-code;         \
	then                                          \
		echo Git working copy is clean...;        \
	else                                          \
		echo ERROR: Git working copy is dirty!;   \
		echo Commit your changes and try again.;  \
		exit -1;                                  \
	fi;

# System Installation ########################################################
.PHONY: develop install download
# Is this section really needed?

develop:
	$(PYTHON) setup.py develop

install:
	$(PYTHON) setup.py install

download:
	$(PIP) install $(PROJECT)
