#!/usr/bin/env sh

pip install --quiet -r requirements.txt -r requirements-dev.txt

echo 'Run pep8 checks'
flake8 start.py loco_sound

echo '\nRun mypy checks'
mypy start.py loco_sound

echo '\nRun tests'
coverage run

echo '\nGenerate coverage report'
coverage html
coverage report

echo '\nBuild HTML docs'
make -C docs/ --quiet html
