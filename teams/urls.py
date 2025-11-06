'''
---------------------------------------------
 File: teams/urls.py
 
URL-Routing der App "teams". Wird im Projekt unter
path("teams/", include("teams.urls", namespace="teams"))
eingehängt. Enthält:
- HTML-Dashboard (serverseitig gerendert)
- JSON-Endpoint fürs Frontend (AJAX)

 Hinweise:
- app_name ermöglicht Namespacing in Templates: {% url 'teams:dashboard' %}
- Die Pfade hier sind relativ zum Präfix „/teams/“ des Projekts.
# ---------------------------------------------
'''
from django.urls import path
from . import views


app_name = "teams" # wichtig für {% url 'teams:…' %}


urlpatterns = [
# GET /teams/ → HTML-Seite mit Filtern, Chart, Matchday
path("", views.league_dashboard, name="dashboard"),


# GET /teams/data/?… → JSON-Payload für AJAX-Updates im Frontend
path("data/", views.league_dashboard_data, name="dashboard_data"),
]