"""
URL configuration for ViolaLab project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


'''
---------------------------------------------


Zentrale URL-Konfiguration für das ganze Django-Projekt.
Bindet Admin, Auth (Login/Logout), die App „teams“ sowie eine Startseite (navigator) ein.
Wichtige Punkte:
- Reihenfolge der Einträge ist relevant: Django prüft sie von oben nach unten.
- include('teams.urls', namespace='teams') hängt die App-Routen unter /teams/ ein.
- Die Class-Based-Views LoginView/LogoutView werden mit as_view() eingebunden.
- Für LogoutView steuert next_page die Zielseite nach dem Logout.
 ---------------------------------------------
'''
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from core.views import navigator


urlpatterns = [
            # Admin-Backend: /admin/
            path("admin/", admin.site.urls),


            # App „teams“ unter /teams/ einhängen (mit Namespace „teams“)
            path("teams/", include(("teams.urls", "teams"), namespace="teams")),


            # Auth: Login/Logout
            path(
            "accounts/login/",
            LoginView.as_view(template_name="auth/login.html"),
            name="login",
            ),
            path(
            "accounts/logout/",
            LogoutView.as_view(next_page="login"), # nach Logout zurück zur Loginseite
            name="logout",
            ),


            # Startseite (Root "/"): einfacher Navigator aus der core-App
            path("", navigator, name="navigator"),
]

