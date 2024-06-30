#!/bin/bash
set -euo pipefail

echo "🖥️  Running installation script, you may asked for sudo password"
echo ""

# Check for python
if [[ "$(python3 -V)" =~ "Python 3.10" ]]
then
    echo "🐍 Python 3.10 detected, skipping install"
else
    echo "🐍 Python 3.10 not found, beginning installation"
fi
echo ""

# Upgrade pip
python -m pip install --upgrade pip

# Check for pipenv
if ! command -v "$(python3 -m pipenv &> /dev/null)" 
then 
    echo "🌱 Pipenv detected, skipping install"
else
    echo "🌱 Pipenv not found, beginning installation"
    python3 -m pip install pipenv
fi
echo ""

# Setting up pipenv
python3 -m pipenv install --dev