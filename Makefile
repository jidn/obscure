# This helps with creating local virtual environments, requirements,
# syntax checking, running tests, coverage and uploading packages to PyPI.
# Homepage at https://github.com/jidn/python-Makefile
#
# This also works with Travis CI
#
# PACKAGE = Source code directory or leave empty
PACKAGE = src
TESTDIR = tests
PROJECT :=
VENV = venv
# Override by putting on commandline:  python=python3.8
python = python
PEP8_IGNORE := E501,E123
PEP257_IGNORE := D104,D203
##############################################################################
ifdef TRAVIS
	VENV = $(VIRTUAL_ENV)
endif
# System paths
BIN := $(VENV)/bin
OPEN := xdg-open

# virtualenv executables
PIP := $(BIN)/pip
TOX := $(BIN)/tox
PYTHON := $(BIN)/$(python)
FLAKE8 := $(BIN)/flake8
PEP257 := $(BIN)/pydocstyle

# Project settings
PKGDIR := $(or $(PACKAGE), ./)
SETUP_PY := $(wildcard setup.py)
SOURCES := $(wildcard *.py)
EGG_INFO := $(subst -,_,$(PROJECT)).egg-info

### Main Targets #############################################################
.PHONY: all env ci help
all: check test

# Target for Travis
ci: test

venv: $(PIP)
$(PIP):
	# Create the virtual enviornment
	$(info "Environment is $(VENV)")
	python -m venv $(VENV)
	$(PIP) install --upgrade pip
	@# pip install the requirements/base.txt
	@test -f requirements/base.txt && $(PIP) install -qr requirements/base.txt || true
	@# With pyproject.toml, pip install this directory as editable
	@test -f pyproject.toml && $(PIP) install -qe . || true
	@# public service announcement
	@echo "Remember to activate the virtual environment."
	@echo "  . venv/bin/activate"

pip: $(PIP)
	pip install --upgrade -r requirements/$(lastword $(MAKECMDGOALS))

help:
	@echo "venv       Create virtual environment and install requirements"
	@echo "             python=PYTHON_EXE   interpreter to use, default=python"
	@echo "pip FILE   Install requirements/FILE"
	@echo "check      Run style checks"
	@echo "test       $(TESTDIR)"/
	@echo "coverage   Get coverage information, optional 'args' like test"
	@echo "tox        Test against multiple versions of python"
	@echo "upload     Upload package to PyPI"
	@echo "clean clean-all  Clean up and clean up removing virtualenv"

### Static Analysis & Travis CI ##############################################
.PHONY: check flake8 pep257
check: flake8 pep257

$(FLAKE8): $(PIP)
	$(PIP) install --upgrade flake8 pydocstyle

flake8: $(FLAKE8)
	$(FLAKE8) $(or $(PACKAGE), $(SOURCES)) $(TESTDIR) --ignore=$(PEP8_IGNORE)

pep257: $(FLAKE8)
	$(PEP257) $(or $(PACKAGE), $(SOURCES)) $(ARGS) --ignore=$(PEP257_IGNORE)

### Testing ##################################################################
.PHONY: test tox

test: $(VENV)/bin/py.test
	$(VENV)/bin/py.test

$(VENV)/bin/py.test: $(PIP)
	$(PIP) install -qr requirements/test.txt


.coveragerc:
ifeq ($(PKGDIR),./)
ifeq (,$(wildcard $(.coveragerc)))
	# If PKGDIR is root directory, ie code is not in its own directory
	# then you should use a .coveragerc file to remove the VENV directory
	# from the coverage search.  I'll auto generate one for you.
	$(info Rerun make to discover autocreated .coveragerc)
	@echo -e "[run]\nomit=$(VENV)/*" > .coveragerc; cat .coveragerc
	@exit 1
endif
endif

coverage:
	coverage run -m pytest
	coverage report

tox: $(TOX)
	$(TOX)

$(TOX): $(PIP)
	$(PIP) install tox

### Cleanup ##################################################################
.PHONY: clean clean-env clean-all clean-build clean-test clean-dist

clean: clean-dist clean-test clean-build

clean-env: clean
	-@rm -rf $(VENV)
	-@rm -rf .tox

clean-all: clean clean-env

clean-build:
	@find $(PKGDIR) -name '*.pyc' -delete
	@find $(PKGDIR) -name '__pycache__' -delete
	@find $(TESTDIR) -name '*.pyc' -delete 2>/dev/null || true
	@find $(TESTDIR) -name '__pycache__' -delete 2>/dev/null || true
	-@rm -rf $(EGG_INFO)
	-@rm -rf __pycache__

clean-test:
	-@rm -rf .coverage

clean-dist:
	-@rm -rf dist build

### Release ##################################################################
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

### System Installation ######################################################
.PHONY: develop install download
# Is this section really needed?

develop:
	$(PYTHON) setup.py develop

install:
	$(PYTHON) setup.py install

download:
	$(PIP) install $(PROJECT)
