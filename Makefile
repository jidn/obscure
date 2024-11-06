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
# Override by putting on commandline:  python=3.8
PYTHON :=
PYTHON_VENV:= venv_$(PYTHON)
PEP8_IGNORE := E501,E123
PEP257_IGNORE := D104,D203,D213,D406,D407,D413
VENV = $(VIRTUAL_ENV)
##############################################################################
# System paths
BIN := $(VENV)/bin
OPEN := xdg-open
#
# Executables I expect to exist.  Not python modules
EXECUTABLES = uv
K := $(foreach exec,$(EXECUTABLES),\
        $(if $(shell which $(exec)),some string,$(error "No $(exec) in PATH")))


# virtualenv executables
FLAKE8 := $(VENV)/bin/flake8
PEP257 := $(VENV)/bin/pydocstyle
NOX := $(VENV)/bin/nox
TWINE := $(VENV)/BIN/twine

# Project settings
PKGDIR := $(or $(PACKAGE), ./)
SETUP_PY := $(wildcard setup.py)
SOURCES := $(wildcard *.py)
EGG_INFO := $(subst -,_,$(PROJECT)).egg-info

### Help #####################################################################
help:
	@echo "venv       Create virtual environment and install dependencies"
	@echo "             PYTHON=VERSION ie 3.9, 3.12.7"
	@echo "check      Run style checks"
	@echo "test       Run tests in $(TESTDIR)"/
	@echo "coverage   Get coverage information, optional 'args' like test"
	@echo "nox        Test against multiple versions of python"
	@echo "upload     Upload package to PyPI"
	@echo "clean clean-all  Clean up and clean up removing virtualenv"

### Main Targets #############################################################
.ONESHELL:
.PHONY: all env ci help
all: check test

# Target for Travis
ci: test

venv:
	# Create the virtual enviornment
ifeq ($(PYTHON),)
		@echo "create using default python"
		@uv venv $(PYTHON_VENV)
else
		@echo "create using python $(PYTHON)"
		uv venv --python=$(PYTHON) $(PYTHON_VENV)
endif
	# Activate the virtual environment for the correct version
	. $(PYTHON_VENV)/bin/activate

	@# Install project dependencies
	@test -f pyproject.toml && uv pip install -r pyproject.toml --extra dev || true
	@# Install directory as editable
	@test -f pyproject.toml && uv pip install -e . || true
	@# Public Service Announcement
	@echo "Remember to activate the virtual environment."
	@echo "  . $(PYTHON_VENV)/bin/activate"

### Static Analysis & Travis CI ##############################################
.PHONY: check flake8 pep257
check: flake8 pep257

$(FLAKE8):
	uv pip install --upgrade flake8 pydocstyle

flake8: $(FLAKE8)
	$(FLAKE8) $(or $(PACKAGE), $(SOURCES)) $(TESTDIR) --ignore=$(PEP8_IGNORE)

pep257: $(FLAKE8)
	$(PEP257) $(or $(PACKAGE), $(SOURCES)) $(ARGS) --ignore=$(PEP257_IGNORE)

### Testing ##################################################################
.PHONY: test nox

test: $(VENV)/bin/py.test
	$(VENV)/bin/py.test

$(VENV)/bin/py.test:
	@test -f pyproject.toml && uv pip install -r pyproject.toml --extra dev || true


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
	# You should be using src/  See .coveragerc target
	coverage run -m pytest
	coverage report --show-missing

nox: $(NOX)
	$(NOX)

$(NOX):
	uv pip install --upgrade nox

### Cleanup ##################################################################
.PHONY: clean clean-env clean-all clean-build clean-test clean-dist

clean: clean-dist clean-test clean-build

clean-env: clean
	rm -rf venv_*
	rm -rf .nox

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

### Packaging ##################################################################
# For more information on creating packages for PyPI see the writeup at
# http://peterdowns.com/posts/first-time-with-pypi.html
.PHONY: authors register dist upload .git-no-changes

authors:
	echo "Authors\n=======\n\nA huge thanks to all of our contributors:\n\n" > AUTHORS.md
	git log --raw | grep "^Author: " | cut -d ' ' -f2- | cut -d '<' -f1 | sed 's/^/- /' | sort | uniq >> AUTHORS.md

register:
	$(PYTHON_BIN) setup.py register -r pypi

build:
	python -m build

upload-test: $(TWINE)
	python -m twine check --strict dist/*
	python -m twine upload --repository testpypi --config-file ~/.pypirc dist/*

$(TWINE):
	uv pip install --upgrade twine

upload: .git-no-changes register
	$(PYTHON_BIN) setup.py sdist upload -r pypi
	$(PYTHON_BIN) setup.py bdist_wheel upload -r pypi

.git-no-changes:
	@if git diff --name-only --exit-code;         \
	then                                          \
		echo Git working copy is clean ...;         \
	else                                          \
		echo ERROR: Git working copy is dirty!;     \
		echo Commit your changes and try again.;    \
		exit -1;                                    \
	fi;
