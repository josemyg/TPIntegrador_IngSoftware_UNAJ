#!/usr/bin/env bash

python manage.py makemigrations --noinput
python manage.py migrations --noinput
python manage.py createsuperuser --noinput 
python manage.py collecstatic --noinput
python -m gunicorn --bind 0.0.0.0:8000 --workers 3 tp_integrador.wsgi:application