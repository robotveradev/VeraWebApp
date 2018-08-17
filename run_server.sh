#!/bin/sh
# Collect static in one directory for nginx
python3 manage.py collectstatic --noinput
# Wait for database
#TODO wait for signal, not sleep
sleep 10
# Apply migrations if exists
python3 manage.py migrate
python3 manage.py migrate statistic --database=statistic
# Load initial data
python3 manage.py loaddata actions.json countries.json fixtures.json languages.json spec.json keys.json
# Run gunicorn server
gunicorn vera.wsgi:application -b 0.0.0.0:9999
