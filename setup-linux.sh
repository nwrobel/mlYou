#!/bin/bash
set -e

rm -rf py-venv-linux
python3 -m venv py-venv-linux
source ./py-venv-linux/bin/activate
pip install -r requirements.txt