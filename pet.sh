#!/bin/bash


SCRIPT_PATH=$(dirname "$(realpath "$0")")


PYTHON_SCRIPT="$SCRIPT_PATH/main.py"


VENV_PYTHON="$SCRIPT_PATH/env/bin/python"



# Run the Python script in detached mode using nohup
nohup "$VENV_PYTHON" "$PYTHON_SCRIPT" >/dev/null 2>&1 &
