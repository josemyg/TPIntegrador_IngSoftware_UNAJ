import os, sys
sys.path.insert(0, r"c:\Users\jenib\Proyectos\TPIntegrador_IngSoftware_UNAJ")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tp_integrador.settings')
import django
from django.urls import URLPattern, URLResolver

django.setup()
from tp_integrador import urls as root_urls


def list_urls(patterns, prefix=''):
    out = []
    for p in patterns:
        if isinstance(p, URLPattern):
            out.append(prefix + str(p.pattern))
        elif isinstance(p, URLResolver):
            out.extend(list_urls(p.url_patterns, prefix + str(p.pattern)))
    return out

for u in list_urls(root_urls.urlpatterns):
    if 'pagos' in u:
        print(u)
