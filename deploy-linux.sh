rm -rf ./py-venv
virtualenv -p python3 ./py-venv
source py-venv/bin/activate
pip install -r ./requirements.txt