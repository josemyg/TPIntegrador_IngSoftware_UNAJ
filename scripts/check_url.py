import os, sys
# Ensure project root is on sys.path
sys.path.insert(0, r"c:\Users\jenib\Proyectos\TPIntegrador_IngSoftware_UNAJ")
os.environ.setdefault('DJANGO_SETTINGS_MODULE','tp_integrador.settings')
import django
from django.urls import resolve, Resolver404

django.setup()

from django.test import Client

try:
    m = resolve('/pagos/nuevoPago/')
    print('view func:', m.func)
    print('view_name:', m.view_name)
    print('url_name:', m.url_name)
    print('app_names:', m.app_names)
except Resolver404:
    print('Resolver404')

# Use test client to GET the page
c = Client()
resp = c.get('/pagos/nuevoPago/')
print('Status code:', resp.status_code)
print('Content length:', len(resp.content))
if resp.status_code != 200:
    print('Response content (first 500 chars):')
    print(resp.content[:500].decode(errors='replace'))
