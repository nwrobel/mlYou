#!/bin/sh

if [ $# -eq 0 ]
  then
    echo "Commit message required"
    exit
fi

# remove secrets
python manage_secrets.py remove

# remove the pycache files before pushing and supress output
find . -name \*.pyc -delete > /dev/null; 
git add --all;
git commit -am "$1";
git push origin;