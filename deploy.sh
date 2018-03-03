mkdir -p ~/venvs
cd ~/venvs
rm -rf mlu-env
virtualenv -p python3 mlu-env
source mlu-env/bin/activate

PROJDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pip install -r $PROJDIR/requirements.txt