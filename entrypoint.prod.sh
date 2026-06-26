#!/usr/bin/env bash

python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py createsuperuser --noinput
python manage.py collectstatic --noinput
python -m gunicorn --bind 0.0.0.0:8000 --workers 5 tp_integrador.wsgi:application