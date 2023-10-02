#! /usr/bin/env bash
deactivate
sudo apt install git-flow
sudo apt install python3
sudo apt install python3.11
sudo apt install python3.11-distutils
pip3 install --upgrade pip

rm -rf .venv
pip install virtualenv
pip install pip-tools
python3 -m virtualenv .venv --python=python3.11
printf "\n===============================================\nVirtual python environment has been created.\n"
source .venv/bin/activate
printf "Virtual python environment has been activated.\n"
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
printf "Compiling requirements... This may take a few minutes.\n"
pip-compile ./requirements/development.txt --output-file ./full-requirements.txt --resolver=backtracking --strip-extras
pip install -r ./full-requirements.txt
deactivate
pip uninstall pip-tools -y
source .venv/bin/activate

printf "Done installing requirements for local .venv!\nHave fun coding!\n"
