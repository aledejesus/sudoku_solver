#!/bin/bash
echo '---- UNIT TESTS ----'
coverage run manage.py test -v 2
coverage report
echo
echo '---- FLAKE8 ----'
flake8 .

if [ "$1" == 'choco' ] # checkout .coverage
  then
    git checkout -- .coverage
fi
