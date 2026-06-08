python3 manage.py collecstatic --noinput
python3 manage.py makemigrations --noinput
python3 manage.py migrations --noinput
python3 manage.py createsuperuser --noinput 
python3 -m gunicorn --bind 0.0.0.0:8000 --workers 3 golahora.yedro.ar