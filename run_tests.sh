#!/usr/bin/env sh

pip install --quiet -r requirements.txt -r requirements-dev.txt

echo 'Run pep8 checks'
flake8 .

echo '\nRun mypy checks'
mypy start.py loco_sound

echo '\nBuild HTML docs'
make -C docs/ --quiet html
