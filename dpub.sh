#!/bin/sh -e

# Always run in virtual environment. Create it if needed
if [ -z "$VIRTUAL_ENV" ]; then
    [ -d "$(dirname "$0")/venv" ] || (cd "$(dirname "$0")" && python3 -m virtualenv -p python3 venv && venv/bin/pip3 install -r "$(dirname "$0")"/requirements.txt) 
fi

"$(dirname "$0")"/venv/bin/python3 "$(dirname "$0")"/main.py "$@"