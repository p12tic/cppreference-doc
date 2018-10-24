#!/bin/sh

flake8 --config=config/flake8rc *.py commands index_transform gadgets/standard_revisions_tests/*.py tests
pylint --rcfile=config/pylintrc *.py commands index_transform gadgets/standard_revisions_tests/*.py tests
python3 -m unittest discover "$@"
