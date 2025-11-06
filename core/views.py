from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import logout

@login_required
def navigator(request):
    """
    startseite nach login mit kacheln/links zu bereichen
    """
    return render(request, "core/navigator.html")

def logout_get(request):
    logout(request)              # session sauber beenden
    return redirect("login")   