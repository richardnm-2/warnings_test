#!/bin/bash

pytest --cov-report term --cov --cov-report html:src/tests/coverage
# pytest --cov-report term --cov
# --cov-report term --cov-report xml:coverage.xml
