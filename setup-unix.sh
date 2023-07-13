#! /usr/bin/env bash
sudo apt install git-flow
sudo apt install python3
sudo apt install python3.11
pip3 install --upgrade pip

rm -rf .venv
pip install virtualenv
pip install pip-tools
python3 -m virtualenv .venv --python=python3.11
printf "\n===============================================\nVirtual python environment has been created.\n"
source .venv/bin/activate
printf "Virtual python environment has been acivated.\n"

pip-compile ./requirements/development.txt --output-file ./full-requirements.txt --resolver=backtracking
pip install -r ./full-requirements.txt
deactivate
pip uninstall pip-tools -y
source .venv/bin/activate

printf "Done installing requirements for local .venv!\nHave fun coding!\n"
