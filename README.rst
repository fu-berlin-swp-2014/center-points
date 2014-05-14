centerpoints
============

This is an university software project from students of the FU Berlin. We
plan to implement different algorithms to approximate centerpoints.

Development Setup
=================

Run all commands in the root directory of the repository.

Setup virtualenv and install all requirements.
``$ setup_virtualenv.sh``

Load virtualenv into your shell:
``$ source ./env/bin/active``

To run the tests
``$ nosetests``

Emulate a travis test run. This will run the tests and build the documentation.
If this pass, travis-ci should pass as well.
``$ ./travis.sh``

Documentation
==============

The Documentation is available under: http://centerpoints.readthedocs.org/
