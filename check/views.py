from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.


from tools.confman import get_lang, get_conf
from prepare.tools import delete_temp_files
from science.tools import new_entry
import login.models
import tools.global_alerts
import datetime
import check.tools


UNIVERSAL_LANG = get_lang(sections=["universal"])

def GreenCaseView(request):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    check_lang = get_lang(sections=["check"])

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'back': UNIVERSAL_LANG["universal"]["back"],
        'check': check_lang["check"]
    }
    user = login.models.User.objects.filter(pk=request.session['UserId'])[0]
    new_entry("g1", user.getAnonId(request.session['PrivKey']), "check")
    return render(request, 'check/green_case.html', args)


def WellFeelingView(request):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    check_lang = get_lang(sections=["check"])

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'back': UNIVERSAL_LANG["universal"]["back"],
        'check': check_lang["check"]
    }

    return render(request, 'check/well_feeling.html', args)


def SaveMePlanView(request):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    check_lang = get_lang(sections=["check"])

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'back': UNIVERSAL_LANG["universal"]["back"],
        'check': check_lang["check"]
    }

    return render(request, 'check/save_me_plan.html', args)


def PracticeSelfCareView(request):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    check_lang = get_lang(sections=["check"])

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'back': UNIVERSAL_LANG["universal"]["back"],
        'check': check_lang["check"]
    }

    return render(request, 'check/practice_self_care.html', args)

def CheckupView(request):
    """Daily checkup page where user says how their day is. Using method GET for value."""
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    check_lang = get_lang(sections=["check"])
    day = datetime.date(2020, 12, 12)

    if request.GET:
        if 'day' in request.GET.keys():
            if request.GET['day'] in ['red', 'orange', 'green']:  # Check if user has manipulated values.
                user = login.models.User.objects.filter(pk=request.session['UserId'])[0]
                symkey = user.getSymKey(request.session['PrivKey'])
                today = datetime.date.today()
                check.tools.fillcheck(user, symkey)

                all_checks = user.check_set.order_by('CheckId').reverse()
                if len(all_checks) > 0:
                    last_check = all_checks[0]
                else:
                    last_check = None

                if last_check and last_check.getDate() == today:
                    check_entry = last_check
                else:
                    try:
                        check_entry = user.check_set.create(Date=today)
                    except Exception as e:
                        tools.global_alerts.add_alert(request, 'warning', UNIVERSAL_LANG['universal']['error'], check_lang['check']['could_not_save'])
                        check_entry = None

                if check_entry:
                    try:
                        check_entry.setRating(symkey, request.GET['day'])
                        check_entry.save()
                        tools.global_alerts.add_alert(request, 'success', UNIVERSAL_LANG['universal']['success'], check_lang['check']['could_save'])
                        return HttpResponseRedirect(reverse('check:green-case'))

                    except Exception as e:
                        check_entry.delete()
                        tools.global_alerts.add_alert(request, 'warning', UNIVERSAL_LANG['universal']['error'], check_lang['check']['could_not_save'])
                new_entry("c1", user.getAnonId(request.session['PrivKey']), request.GET['day'])
            else:
                tools.global_alerts.add_alert(request, 'warning', UNIVERSAL_LANG['universal']['error'], check_lang['check']['could_not_save'])

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'check': check_lang["check"]
    }

    return render(request, 'check/checkup.html', args)
