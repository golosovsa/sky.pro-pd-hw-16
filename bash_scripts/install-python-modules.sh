#!/bin/bash

# 0. create venv
python3 -m venv venv

# 1. activate venv
source venv/bin/activate

# 2. install python requirement modules
venv/bin/python3 -m pip install --upgrade pip psycopg2-binary flask sqlalchemy flask-sqlalchemy python-dotenv

# 3. rewrite requirements.txt
venv/bin/python3 -m pip freeze > requirements.txt
