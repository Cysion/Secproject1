from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.

from tools.confman import get_lang  # Needed for retrieving text from language file

UNIVERSAL_LANG = get_lang(sections=["universal"])  # Needed to get universal lang texts.

def ClientsView(request):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    # YOUR CODE HERE

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
    }

    return render(request, 'professionals/clients.html', args)

def saveMePlanView(request, UserId):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    # YOUR CODE HERE

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
    }

    return render(request, 'professionals/savemeplan.html', args)

def CheckView(request, UserId):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    # YOUR CODE HERE

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
    }

    return render(request, 'professionals/check.html', args)
