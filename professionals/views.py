from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

import userprofile.tools
import login.models
import prepare.tools
import prepare.models
import datetime
import savemeplan.tools

from calendar import monthrange
from datetime import date
# Create your views here.

from tools.confman import get_lang  # Needed for retrieving text from language file
from prepare.tools import delete_temp_files

UNIVERSAL_LANG = get_lang(sections=["universal"])  # Needed to get universal lang texts.

def ClientsView(request):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))
    elif request.session["Role"] == "User":
        return HttpResponseRedirect(reverse('userprofile:Profile'))

    delete_temp_files(request.session)

    clients_lang = get_lang(sections=["professionals"])
    # YOUR CODE HERE
    """ Clients should be a list with dicts. With following keys:
    FirstName (string), LastName (string),
    Permissions (dict) with key as Profile, SaveMePlan, Check, Prepare or Media
    Values as 1 or 0 where 1 is got access and 0 denied access."""

    userprofile.tools.update_relation_to(request.session['UserId'], request.session['PrivKey'])
    clients = userprofile.tools.show_all_relations_from(request.session['UserId'], request.session['PrivKey'])

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



def profile_view(request, UserId):
    if not 'UserId' in request.session.keys():
        return HttpResponseRedirect(reverse('login:Login'))
    elif request.session["Role"] == "User":
        return HttpResponseRedirect(reverse('userprofile:Profile'))

    delete_temp_files(request.session)

    try:
        userPrivKey = userprofile.tools.shares_data_with(UserId, request.session['UserId'], request.session['PrivKey'], 'profile').decode("utf-8")
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
    elif request.session["Role"] == "User":
        return HttpResponseRedirect(reverse('userprofile:Profile'))

    delete_temp_files(request.session)

    prep = userprofile.tools.shares_data_with(UserId, request.session['UserId'], request.session['PrivKey'], 'prepare')
    media = userprofile.tools.shares_data_with(UserId, request.session['UserId'], request.session['PrivKey'], 'media')

    if not prep and not media:
        return HttpResponseRedirect(reverse('professionals:clients'))

    user=login.models.User.objects.filter(UserId=UserId)[0]
    permissions = userprofile.tools.get_permissions(UserId, request.session['UserId'], request.session['PrivKey'])
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
            contacts=prepare.tools.show_contacts(user.getUid(), userPrivKey)
            template = 'prepare/5_contacts.html'
        elif page == 6:
            template = 'prepare/6_wheretocall.html'
        elif page == 7:
            symKey = user.getSymKey(userPrivKey)
            diary = prepare.tools.show_diary(user.getUid(), symKey, 'Diary', request.session['UserId'])
            template = 'prepare/7_diary.html'
        elif page == 8:
            symKey = user.getSymKey(userPrivKey)
            if request.method == 'POST':
                if 'date' in request.POST.keys() and 'text' in request.POST.keys():
                    now = str(datetime.datetime.now())
                    diaryEntry = prepare.models.Diary(UserId = user)
                    print(f"'{login.models.User.objects.filter(UserId=request.session['UserId'])[0].getName(request.session['PrivKey'])}'")
                    diaryEntry.setAuthorId(symKey, request.session['UserId'])
                    diaryEntry.setAuthor(symKey, str(login.models.User.objects.filter(UserId=request.session['UserId'])[0].getName(request.session['PrivKey'])))
                    diaryEntry.setDate(symKey, request.POST['date'])
                    text = request.POST['text'] if len(request.POST['text']) <= 500 else request.POST['text'][0:500]
                    diaryEntry.setEntryType(symKey, 'Notes')
                    diaryEntry.setText(symKey, text)
                    diaryEntry.setTimestamp(symKey, now)
                    diaryEntry.save()
            diary = prepare.tools.show_diary(user.getUid(), symKey, 'Notes', request.session['UserId'])
            template = 'prepare/8_therapynotes.html'
        elif page == 3 or page == 4:
            pass
        else:
            return HttpResponseRedirect(reverse('professionals:clients'))
        prep = True

    if media:
        userPrivKey = media.decode("utf-8")

        if page == 3:
            memories = prepare.tools.show_all_memories(user.getUid(), userPrivKey, 's')
            template = 'prepare/3_supportivememories.html'
        elif page == 4:
            memories = prepare.tools.show_all_memories(user.getUid(), userPrivKey, 'd')
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
    elif request.session["Role"] == "User":
        return HttpResponseRedirect(reverse('userprofile:Profile'))

    savemeplan_lang = get_lang(sections=['savemeplan'])

    STEP_COLORS = {  # Main color for that step.
        'A1': '#f77979',
        'A2': '#ff9cf2',
        'A3': '#cfcfcf',
        'A4': '#f7c074',
        'B1': '#c2904e',
        'B2': '#8bff87',
        'B3': '#adf8ff',
        'B4': '#88b9eb',
        'C1': '#50cc68',
        'C2': '#5f85d9',
        'C3': '#52e8ff',
        'C4': '#ff4040',
    }

    STEP_TITLES = {
        'A1': savemeplan_lang['savemeplan']['mysit'],
        'A2': savemeplan_lang['savemeplan']['myemo'],
        'A3': savemeplan_lang['savemeplan']['mytho'],
        'A4': savemeplan_lang['savemeplan']['mybeh'],
        'B1': savemeplan_lang['savemeplan']['calm'],
        'B2': savemeplan_lang['savemeplan']['rout'],
        'B3': savemeplan_lang['savemeplan']['repl'],
        'B4': savemeplan_lang['savemeplan']['prot'],
        'C3': savemeplan_lang['savemeplan']['gosafe'],
    }

    delete_temp_files(request.session)


    title = savemeplan_lang['savemeplan']['title']

    try:
        userPrivKey = userprofile.tools.shares_data_with(UserId, request.session['UserId'], request.session['PrivKey'], 'saveMePlan').decode("utf-8")
    except AttributeError:
        return HttpResponseRedirect(reverse('professionals:clients'))
    if not userPrivKey:
        return HttpResponseRedirect(reverse('professionals:clients'))
    user = login.models.User.objects.filter(UserId=UserId)[0]
    symkey = user.getSymKey(userPrivKey)
    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    entries = savemeplan.tools.get_all_savemeplan_items(user, symkey)

    for session in entries.values():
        for key, step in session.items():
            if key != 'Datetime':
                step['Color'] = STEP_COLORS[step['Key']]
                step['Title'] = STEP_TITLES[step['Key']]

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'content': entries,
        'title': title,
        'name': f"{user.getFirstName(userPrivKey)} {user.getLastName(userPrivKey)}",
        'prof': True,
        'template': 'base_professionals.html'
    }

    return render(request, 'savemeplan/savemeplan_history.html', args)

def CheckView(request, UserId):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))
    elif request.session["Role"] == "User":
        return HttpResponseRedirect(reverse('userprofile:Profile'))

    delete_temp_files(request.session)

    try:
        userPrivKey = userprofile.tools.shares_data_with(UserId, request.session['UserId'], request.session['PrivKey'], 'profile').decode("utf-8")
    except AttributeError:
        return HttpResponseRedirect(reverse('professionals:clients'))
    if not userPrivKey:
        return HttpResponseRedirect(reverse('professionals:clients'))

    check_lang = get_lang(sections=["check"])
    user = login.models.User.objects.filter(UserId=UserId)[0]
    symkey = user.getSymKey(userPrivKey)

    calendar = { # Calendar variables
        'days': [],
        'year': '',
        'month': ''
    }

    if request.method == 'POST': # Searched month & year
        if request.POST.keys():
            if 'month' and 'year' in request.POST.keys():

                calendar['year'] = request.POST['year']
                calendar['month'] = request.POST['month']

                first_date = datetime.date(int(request.POST['year']), int(request.POST['month']), 1) # First day in the month
                num_days = monthrange(int(request.POST['year']), int(request.POST['month'])) # Number of days in month
                last_date = datetime.date(int(request.POST['year']), int(request.POST['month']), num_days[1]) # Last day in month

                calendar['days'].append(num_days[1]) # Provide number of days in month for calendar

                for day in range(num_days[1]): # Prepare slots for each day
                    calendar['days'].append('')

                objects = user.check_set.filter(Date__range=(first_date, last_date)) # Retrieve data from database

                for day in objects: # Fill in data into calendar
                    calendar['days'].insert(day.getDate().day, day.getRating(symkey))

    else:

        today = datetime.date.today()
        calendar['year'] = today.year
        calendar['month'] = today.month

        first_date = datetime.date(today.year, today.month, 1) # First day in the month
        num_days = monthrange(today.year, today.month) # Number of days in month
        last_date = datetime.date(today.year,today.month, num_days[1]) # Last day in month

        calendar['days'].append(num_days[1]) # Provide number of days in month for calendar

        for day in range(num_days[1]): # Prepare slots for each day
            calendar['days'].append('')

        objects = user.check_set.filter(Date__range=(first_date, last_date)) # Retrieve data from database

        for day in objects: # Fill in data into calendar
            calendar['days'].insert(day.getDate().day, day.getRating(symkey))


    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'back': UNIVERSAL_LANG["universal"]["back"],
        'check': check_lang["check"],
        'calendar': calendar,
        'template' : 'base_professionals.html'
    }

    return render(request, 'check/green_case.html', args)
