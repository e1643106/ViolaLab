import re # RegEx can be used to check if a string contains the specified search pattern
from django.conf import settings 
from django.shortcuts import redirect # hilfsfunktion, um schnell eine HTTP 302 redirect-antwort zu bauen (HttpResponseRedirect)
from urllib.parse import quote
from django.shortcuts import resolve_url





# middlware ist code, der zwischen dem request und der view bzw zwischen view un response ausgeführt wird
# quasi eine kette:
# htttp request kommt rein
# django schickt durch alle middlewares
# dann erreicht er einen view
# danach geht die response wieder rückwärts durch die middleware 



# Middleware Klasse , callable , mit Klassen __init__ , __call__
class LoginRequiredMiddleware:
    """
    erzwingt login auf allen seiten, außer explizit ausgenommenen pfaden
    """
    def __init__(self, get_response):   # __init__ wir einmal beim Serverstart aufgerufen , self ist referenz auf die Instanz der Klasse  ... 
                                        # um auf eigene Attribute/Funktionen zuzugriefen,...python oop
        self.get_response = get_response # get_response ist ein callable , das Django der Middleware übergibt. es repräsentier "den nächsten Schritt" in der
                                         # moddleware-kette ( nächste middleware , am ende ..die view)
                                         # warum self.get.... = get_response , es speichert dieses cllabble auf der instanz , damit es später in
                                         # __call__ aufrugbar ist, falls die Anfrage duchgelassenw erden soll: return selg.get_response(request)   


        # Standard-Ausnahmen (Login, Logout, Admin, Static)
        # ^ anfang des strings
        # $ ende 
        # .* bel. viele Zeichen
        default_exempt = [
            r"^accounts/login/$",
            r"^accounts/logout/$",
            r"^admin/.*",
            r"^static/.*",
        ] # diese pfade brauchen keinen login 

        # getattr(settings, "LOGIN_EXEMPT_URLS", []) holt settings.LOGIN_EXEMPT_URLS, oder [] , falls nicht gesetzt
        # so kann man später im Projekt weitere Regeln ergänzen , ohne Middleware Datei zu ändern 
        extra = getattr(settings, "LOGIN_EXEMPT_URLS", [])

        # kompiliert die Regexe einmal beim Start, nicht bei jeder Anfrage neu ( performance..)
        # Ergebnis ist eine Liste aus Regex Objekten .match()
        self.exempt_urls = [re.compile(x) for x in (default_exempt + list(extra))]



    def __call__(self, request): # Macht die Instanz aufrufbar wie ein Funktion, Django ruft für jede Anfrage diese Methode aus
                                  # Signatur: bekommt einen HttpRequest, muss eine HttpResponse zurückgeben

        path = request.path.lstrip("/") # request.path : z.b.: /admin/login..., lstrip("/"") entfernt den führenden Slash , sodass der Regex "âdmin/.*"
                                       # passt der ^bezieht sich auf den ersten Buchstaben des Pfades nicht /


        # Wenn Pfad ausgenommen ist -> durchlassen
        # any(..) prüft: mindestens ein REgex m passt am Anfang ( match, nicht search) des path.
        # Falls ja: Nichts zu tun -> Anfrage an die nächste Middleware/View weiterrreichen
        if any(m.match(path) for m in self.exempt_urls):
            return self.get_response(request)
        

        # Wenn eingeloggt -> durchlassen
        # nucht die AuthentucationMiddleware (die vorher laugen muss), die request.user setzt.
        # ist der user eingeloggt (True), gibts keinen Zwang zum Login -> weiterreichen
        if request.user.is_authenticated:
            return self.get_response(request)
        


        # sonst zum Login umleiten (mit next=...)
        # liest Login-Ziel aus den Settings (bei dir: "/accounts/login/")
        # liefert den angefragten Pfad inkl. Querystring, z. B. "/teams/search/?q=ä ö&x=1".
        login_url = resolve_url(settings.LOGIN_URL)
        next_param = quote(request.get_full_path(), safe="/")
        return redirect(f"{login_url}?next={next_param}")
