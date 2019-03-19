rm -rf ./py-venv
virtualenv -p python3 ./py-venv
source py-venv/bin/activate

PROJDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pip install -r ./requirements.txt