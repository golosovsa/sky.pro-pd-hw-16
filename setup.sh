#!/bin/bash

if [ ! -f ".env" ]; then
    echo ".env does not exist."
    exit 1
fi

DB_NAME=$(grep DB_NAME .env | cut -d '=' -f 2-)
DB_USER=$(grep DB_USER .env | cut -d '=' -f 2-)
DB_PASSWORD=$(grep DB_PASSWORD .env | cut -d '=' -f 2-)

# run install-postgresql.sh
sudo ./bash_scripts/install-postgresql.sh "$DB_USER" "$DB_PASSWORD" "$DB_NAME"

# run install-python-modules.sh
sudo ./bash_scripts/install-python-modules.sh

# run install_app.py
sudo venv/bin/python3 -m install_app.py