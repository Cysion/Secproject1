from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

import userprofile.tools
import login.models
import prepare.tools
import prepare.models
import datetime
import savemeplan.tools
# Create your views here.

from tools.confman import get_lang  # Needed for retrieving text from language file
from prepare.tools import delete_temp_files

UNIVERSAL_LANG = get_lang(sections=["universal"])  # Needed to get universal lang texts.

def ClientsView(request):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    clients_lang = get_lang(sections=["professionals"])
    # YOUR CODE HERE
    """ Clients should be a list with dicts. With following keys:
    FirstName (string), LastName (string),
    Permissions (dict) with key as Profile, SaveMePlan, Check, Prepare or Media
    Values as 1 or 0 where 1 is got access and 0 denied access."""

    userprofile.tools.updateRelationTo(request.session['UserId'], request.session['PrivKey'])
    clients = userprofile.tools.showAllRelationsFrom(request.session['UserId'], request.session['PrivKey'])

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset


    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'no_clients': clients_lang["professionals"]["long_texts"]["no_clients"],
        'clients': clients,
        'media': clients_lang["professionals"]["media"]
    }

    return render(request, 'professionals/clients.html', args)



def profileView(request, UserId):
    if not 'UserId' in request.session.keys():
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    try:
        userPrivKey = userprofile.tools.sharesDataWith(UserId, request.session['UserId'], request.session['PrivKey'], 'profile').decode("utf-8")
    except AttributeError:
        return HttpResponseRedirect(reverse('professionals:clients'))
    if not userPrivKey:
        return HttpResponseRedirect(reverse('professionals:clients'))
    user=login.models.User.objects.filter(UserId=UserId)[0]

    account = {}
    account['firstName']=user.getFirstName(userPrivKey)
    account['lastName']=user.getLastName(userPrivKey)
    account['gender']=user.getGender(userPrivKey)
    account['email'] = user.getEmail()

    profile_lang = get_lang(sections=["userprofile"])
    login_lang = get_lang(sections=["login"])
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'form': login_lang["login"]["form"],
        'profile': profile_lang["userprofile"]["long_texts"],
        'alerts': login_lang['login']['long_texts']['alerts'],
        "account":account,
        'template': "base_professionals.html",
        'profView': True
    }

    return render(request, 'userprofile/edit.html', args)


def prepareView(request, UserId, page):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    prep = userprofile.tools.sharesDataWith(UserId, request.session['UserId'], request.session['PrivKey'], 'prepare')
    media = userprofile.tools.sharesDataWith(UserId, request.session['UserId'], request.session['PrivKey'], 'media')

    if not prep and not media:
        return HttpResponseRedirect(reverse('professionals:clients'))

    user=login.models.User.objects.filter(UserId=UserId)[0]
    permissions = userprofile.tools.getPermissions(UserId, request.session['UserId'], request.session['PrivKey'])
    prepare_lang = get_lang(sections=["prepare"])
    template = 'prepare/menu.html'
    memories = []
    contacts = []
    diary= []

    if prep:
        userPrivKey = prep.decode("utf-8")

        if page == 1:
            template = 'prepare/1_howto.html'
        elif page == 2:
            template = 'prepare/2_practicebreathing.html'
        elif page == 5:
            contacts=prepare.tools.showContacts(user.getUid(), userPrivKey)
            template = 'prepare/5_contacts.html'
        elif page == 6:
            template = 'prepare/6_wheretocall.html'
        elif page == 7:
            symKey = user.getSymKey(userPrivKey)
            diary = prepare.tools.showDiary(user.getUid(), symKey)
            template = 'prepare/7_diary.html'
        elif page == 8:
            template = 'prepare/8_therapynotes.html'
        elif page == 3 or page == 4:
            pass
        else:
            return HttpResponseRedirect(reverse('professionals:clients'))
        prep = True

    if media:
        userPrivKey = media.decode("utf-8")

        if page == 3:
            memories = prepare.tools.showAllmemories(user.getUid(), userPrivKey, 's')
            template = 'prepare/3_supportivememories.html'
        elif page == 4:
            memories = prepare.tools.showAllmemories(user.getUid(), userPrivKey, 'd')
            template = 'prepare/4_destructivememories.html'
        elif page == 1 or page == 2 or page == 5 or page == 6 or page == 7 or page == 8:
            pass
        else:
            return HttpResponseRedirect(reverse('professionals:clients'))
        media = True


    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'prepare': prepare_lang["prepare"],
        'nav': prepare_lang["prepare"]["nav"],
        'template': "base_professionals.html",
        'memories':memories,
        'contacts':contacts,
        'entries':diary,
        'profView':True,
        'UserId':UserId,
        'prep':prep,
        'media':media
    }

    #if 0 < page < 9:
    #    new_entry("p3", user.getAnonId(request.session['PrivKey']), f"step {page}")
    return render(request, template, args)


def saveMePlanView(request, UserId):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    try:
        userPrivKey = userprofile.tools.sharesDataWith(UserId, request.session['UserId'], request.session['PrivKey'], 'saveMePlan').decode("utf-8")
    except AttributeError:
        return HttpResponseRedirect(reverse('professionals:clients'))
    if not userPrivKey:
        return HttpResponseRedirect(reverse('professionals:clients'))
    user=login.models.User.objects.filter(UserId=UserId)[0]
    symkey=user.getSymKey(userPrivKey)
    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    entries = savemeplan.tools.get_all_savemeplan_items(user, symkey)
    print (entries)
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'content':entries
    }

    return render(request, 'professionals/savemeplan.html', args)

def CheckView(request, UserId):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    try:
        userPrivKey = userprofile.tools.sharesDataWith(UserId, request.session['UserId'], request.session['PrivKey'], 'profile').decode("utf-8")
    except AttributeError:
        return HttpResponseRedirect(reverse('professionals:clients'))
    if not userPrivKey:
        return HttpResponseRedirect(reverse('professionals:clients'))
    user=login.models.User.objects.filter(UserId=UserId)[0]

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
    }

    return render(request, 'professionals/check.html', args)
