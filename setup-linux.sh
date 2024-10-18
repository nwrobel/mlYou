#!/bin/bash
set -e

rm -rf py-venv-linux
python3 -m venv py-venv-linux
source ./py-venv-linux/bin/activate
pip3 install -r requirements.txt