# This helps with creating local virtual environments, requirements,
# syntax checking, running tests, coverage and uploading packages to PyPI.
# Homepage at https://github.com/jidn/python-Makefile
#
# This also works with Travis CI
#
# PACKAGE = Source code directory or leave empty
PACKAGE =
TESTDIR = test
PROJECT :=
ENV = venv
# Override by putting on commandline:  python=python2.7
python = python
REQUIRE = requirements.txt
PEP8_IGNORE := E501,E123
PEP257_IGNORE := D104,D203
##############################################################################
ifdef TRAVIS
	ENV = $(VIRTUAL_ENV)
endif
# System paths
BIN := $(ENV)/bin
OPEN := xdg-open
SYS_VIRTUALENV := virtualenv

# virtualenv executables
PIP := $(BIN)/pip
TOX := $(BIN)/tox
PYTHON := $(BIN)/$(python)
FLAKE8 := $(BIN)/flake8
PEP257 := $(BIN)/pydocstyle
COVERAGE := $(BIN)/coverage
TEST_RUNNER := $(BIN)/py.test
$(TEST_RUNNER): $(PIP)
	$(PIP) install pytest | tee -a $(LOG_REQUIRE)

# Project settings
PKGDIR := $(or $(PACKAGE), ./)
REQUIREMENTS := $(shell find ./ -name $(REQUIRE))
SETUP_PY := $(wildcard setup.py)
SOURCES := $(wildcard *.py)
EGG_INFO := $(subst -,_,$(PROJECT)).egg-info
COVER_ARG := --cov-report term-missing --cov=$(PKGDIR) \
	$(if $(wildcard .coveragerc), --cov-config .coveragerc)

# Flags for environment/tools
LOG_REQUIRE := .requirements.log

### Main Targets #############################################################
.PHONY: all env ci help
all: check test

# Target for Travis
ci: test

env: $(PIP) $(LOG_REQUIRE)
$(PIP):
	$(info "Environment is $(ENV)")
	test -d $(ENV) || $(SYS_VIRTUALENV) --python $(python) $(ENV)

$(LOG_REQUIRE): $(REQUIREMENTS)
	for f in $(REQUIREMENTS); do \
	  $(PIP) install -r $$f | tee -a $(LOG_REQUIRE); \
	done
	touch $@

help:
	@echo "env        Create virtualenv and install requirements"
	@echo "             python=PYTHON_EXE   interpreter to use, default=python"
	@echo "check      Run style checks"
	@echo "test       TEST_RUNNER on '$(TESTDIR)'"
	@echo "             args=\"-x --pdb --ff\"  optional arguments"
	@echo "coverage   Get coverage information, optional 'args' like test"
	@echo "tox        Test against multiple versions of python"
	@echo "upload     Upload package to PyPI"
	@echo "clean clean-all  Clean up and clean up removing virtualenv"

### Static Analysis & Travis CI ##############################################
.PHONY: check flake8 pep257
check: flake8 pep257

$(FLAKE8): $(PIP)
	$(PIP) install --upgrade flake8 pydocstyle | tee -a $(LOG_REQUIRE)

flake8: $(FLAKE8)
	$(FLAKE8) $(or $(PACKAGE), $(SOURCES)) $(TESTDIR) --ignore=$(PEP8_IGNORE)

pep257: $(FLAKE8)
	$(PEP257) $(or $(PACKAGE), $(SOURCES)) $(ARGS) --ignore=$(PEP257_IGNORE)

### Testing ##################################################################
.PHONY: test coverage tox

test: $(TEST_RUNNER)
	$(TEST_RUNNER) $(args) $(TESTDIR)

coverage: $(COVERAGE) .coveragerc
	echo $(TEST_RUNNER) $(args) $(COVER_ARG) $(TESTDIR)

.coveragerc:
ifeq ($(PKGDIR),./)
ifeq (,$(wildcard $(.coveragerc)))
	# If PKGDIR is root directory, ie code is not in its own directory
	# then you should use a .coveragerc file to remove the ENV directory
	# from the coverage search.  I'll auto generate one for you.
	$(info Rerun make to discover autocreated .coveragerc)
	@echo -e "[run]\nomit=$(ENV)/*" > .coveragerc; cat .coveragerc
	@exit 1
endif
endif

$(COVERAGE): $(PIP)
	$(PIP) install pytest-cov | tee -a $(LOG_REQUIRE)

tox: $(TOX)
	$(TOX)

$(TOX): $(PIP)
	$(PIP) install tox | tee -a $(LOG_REQUIRE)

### Cleanup ##################################################################
.PHONY: clean clean-env clean-all clean-build clean-test clean-dist

clean: clean-dist clean-test clean-build

clean-env: clean
	-@rm -rf $(ENV)
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
