import urllib.request
try:
    with urllib.request.urlopen('http://127.0.0.1:8001/pagos/nuevoPago/') as r:
        print('status', r.status)
        html = r.read(300).decode('utf-8', errors='replace')
        print(html)
except Exception as e:
    print('ERROR', repr(e))
