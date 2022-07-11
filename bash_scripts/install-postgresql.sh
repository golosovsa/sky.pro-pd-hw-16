#!/bin/bash

# PostgresSQL install and setup script

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo -e "\nPlease call '$0 <user_name> <user_password> <db_name>' to run this command!\n"
    exit 1
fi

# 0. upgrade all
sudo apt update && sudo apt upgrade -y

# 1. install postgresql
sudo apt install -y postgresql postgresql-contrib

# 2. create database user
sudo -u postgres psql -c "CREATE USER $1 WITH ENCRYPTED PASSWORD '$2';"

# 3. create app database
sudo -u postgres psql -c "CREATE DATABASE $3 WITH ENCODING 'utf-8' OWNER $1;"
