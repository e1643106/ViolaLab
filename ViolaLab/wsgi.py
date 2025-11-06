"""
WSGI config for ViolaLab project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application # importiert django hilfsfunktion , die eine WSGI kompatible anwendung erstellt.
# 'WSGI kompatible'heißt ein OBjekt/Funktion , die das WSGI Protokoll spricht und REquest/Response verarbeiten kann.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ViolaLab.settings')
# setzt die umgebungsvariable DJANGO_SETTINGS_MODULE, falls sie nicht schon existiert
# 'ViolaLab.settings" -> Pfad zu settings
# setdefault: setzt nur wenn ncoh kein Wert existiert, da es in der Prod Umgebung auch explizit gesetzt werden kann

application = get_wsgi_application()
# ruft get_wsgi_application() auf -> erstellt die WSGI Anwendung
# ergebnis ist eine Funktion WSGI- Callable die:
# 1. Request vom Webserver entgegennimmt
# 2. durch Django weiterleitet (Middleware -> URls -> View -> Response)
# 3. und die fertigen Response zurückgibt

# diese variable MUSS application heißen, weil WSGI Server sie genau so erwarten




# Dev (runserver): normalerweise nciht, da laüft django mit ASGI, WSGI ist trotzdem kompatible

#Prod: webserver lädt diese Datei, sucht die Variable application und nutzt sie als einstiegspunlt

