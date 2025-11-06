"""
ASGI config for ViolaLab project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# ASGI: Asynchronous Server Gateway Interface
# Es ist ein Standard, wie Python-Webanwendungen mit Webservern sprechen – asynchron, mit Support für HTTP, WebSockets und Lifespan-Events (Start/Shutdown)


# sagt django wo die eisntellungen liegen, ViolaLab.settings ist pfad zu settings.py
#setdefaiult -> nur setzten, wenn noch nicht vorhanden
# so kann z.B. ein Server oder manage.py das schon vorher gesetzt haben

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ViolaLab.settings')


#baut ASGI app von django (django.core.handlers.asgi.ASGIHandler)
#folgende sachen passieren:
# einstellungen laden (settings.py)
# app-registry aufbauen (alle INSTALLED_APPS)
# AppConfig.ready() Hooks ausführen
# Middleware-Stack bauen (security, Auth, Sessions....)
# Ergebnis ist ein Callable names application, das der ASGI Server ausruft


application = get_asgi_application()



# Der ASGI-Server importiert ViolaLab.asgi und liest die Variable application
# Für jede Anfrage ruft er dieses Objekt auf; Django macht den Rest (Middleware, URLs, View)

