from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import transaction

import login.models
import login.tools
import userprofile.tools
import tools.global_alerts
import datetime

from tools.confman import get_lang
from science.tools import new_entry

UNIVERSAL_LANG = get_lang(sections=["universal"])

def register_view(request):
    '''This view will display the registration page and when submitting a
    registration it will enter here.

    If submitting a registration request.POST will contain the following keys:
        first_name - Users first name
        last_name - Users last name
        date_of_birth - When user was born
        gender - Gender of the user. Is one of the following
            Male
            Female
            Other
        gender_other - If user choose gender=Other this will contain a text.
        email - Users email.
        password - Users entered non hashed password
        repassword - reentered password to dubble check that user entered the
            right one.
        agree_terms - Värdet ska vara "accept"
    '''

    if 'UserId' not in request.session:
        alerts = {}
        
        # Get language text for form.
        login_lang = get_lang(sections=["login"])  
        
        # Check if a user has submitted a form.
        if request.method == 'POST':
            for index in ['first_name','last_name','gender','gender_other', 'email']:
                exceptions = ''
                if index == 'email':
                    exceptions = '1234567890@!#$%&*+-/=?^_`{|}~.'
                if login.tools.contains_bad_char(request.POST[index], exceptions):
                    alerts[index] = "badChar"

            if request.POST["password"] != request.POST["repassword"]:
                alerts['repassword'] = "repassword"
            if len(request.POST["password"]) < 6 or len(request.POST["password"]) > 128:
                alerts["password"] = 'bad_length'
            if login.models.User.objects.filter(Email=request.POST["email"]):
                alerts['email'] = 'email_already_exists'
            if not alerts:
                try:
                    with transaction.atomic():
                        sessionsData = login.tools.register_user(request.POST)

                except AttributeError:
                    alerts['database'] = 'Database error'
                else:
                    request.session['UserId'] = sessionsData[0]
                    request.session['PrivKey'] = sessionsData[1].decode("utf-8")
                    request.session['Role'] = sessionsData[2]
                    request.session['seen_backup'] = 0
                    if request.session['Role'] == 'User':
                        tools.global_alerts.add_alert(
                            request,
                            'info',
                            UNIVERSAL_LANG['universal']['info'],
                            login_lang['login']['long_texts']['alerts']['daily_checkup'],
                            '/check/checkup/'
                        )
                    return HttpResponseRedirect(reverse('userprofile:Backupkey'))

        args = {
            'POST': request.POST,
            'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
            'back': UNIVERSAL_LANG['universal']['back'],
            'form': login_lang["login"]["form"],
            'alerts': login_lang['login']['long_texts']['alerts'],
            'alert': alerts
        }
        return render(request, 'login/register.html', args)
    return HttpResponseRedirect(reverse('userprofile:Profile'))

def login_view(request):
    """This view will display the login page and when submitting login credentials
    it will enter here.

    If submitting login credentials request.POST will contain the following keys:
        email - Users email.
        password - Users entered non hashed password
    """
    if 'UserId' in request.session:
        return HttpResponseRedirect(reverse('userprofile:Profile'))

    login_lang = get_lang(sections=["login"])

    login_fail = False
    if request.method == 'POST':
        try:
            user = login.models.User.objects.filter(Email=request.POST['email'].lower())[0]
        except Exception as e:
            user = None
            login_fail = True

        if user:
            key = login.models.gen_rsa(login.models.secret_scrambler(request.POST["password"], user.getUid()))
            if str(key.publickey().export_key()) == str(user.getPubkey()):
                request.session['UserId'] = user.getUid()
                request.session['PrivKey'] = key.export_key().decode("utf-8")
                request.session['Role'] = user.getRole()
                new_entry("u1", user.getAnonId(request.session['PrivKey']), "na")
                if request.session['Role'] == 'User':
                    tools.global_alerts.add_alert(
                        request,
                        'info',
                        UNIVERSAL_LANG['universal']['info'],
                        login_lang['login']['long_texts']['alerts']['daily_checkup'],
                        '/check/checkup/'
                    )
                    print(user.getName(request.session['PrivKey']))
                    login.tools.survey_time(request, user, request.session['PrivKey'])
                return HttpResponseRedirect(reverse('userprofile:Profile'))
            else:
                login_fail = True
        else:
            login_fail = True

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'post': request.POST,
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'form': login_lang["login"]["form"],
        'alerts': login_lang['login']['long_texts']['alerts'],
        'wrong_login_enterd': login_fail  # A check if right login was entered
    }

    return render(request, 'login/login.html', args)


def forgot_password_view(request):
    """
    Page when user forgot their password.

    POST keys:
        email = users email.
        password = Users new password.
        repassword = Repeated password.
        priv_key = Users backup key / private key used for decrypt of data.

    Alerts for email
        email_dont_exists

    alerts for password
        repassword

    alerts for priv_key
        priv_key
    """
    login_lang = get_lang(sections=["login"])
    alerts = dict()

    if 'UserId' in request.session:
        return HttpResponseRedirect(reverse('userprofile:Profile'))

    if request.method == 'POST':
        if request.POST['password'] == request.POST['repassword']:
            try:
                user = login.models.User.objects.filter(Email=request.POST['email'])[0]
            except Exception as e:
                user = None
            if user:
                try:
                    request.session['UserId'] = user.getUid()
                    request.session["Role"] = user.getRole()
                    request.session['PrivKey']=userprofile.tools.changePass(user.UserId, request.POST['priv_key'], request.POST['password'], request.session["Role"]).decode("utf-8")
                except ValueError as keyError:
                    alerts["relogin"] = "relogin"

                    alert = {
                        "color": "success",  # Check https://www.w3schools.com/bootstrap4/bootstrap_alerts.asp for colors.
                        "title": UNIVERSAL_LANG["universal"]["success"],  # Should mostly be success, error or warning. This text is the bold text.
                        "message": login_lang["login"]["long_texts"]["alerts"]["changed_password_success"]
                    }
                    if "global_alerts" not in request.session.keys():  # Check if global_elerts is in session allready.
                        request.session["global_alerts"] = [alert]
                    else:
                        request.session["global_alerts"].append(alert)

                if 'relogin' not in alerts:
                    return HttpResponseRedirect(reverse('userprofile:Backupkey'))
            else:
                alerts["relogin"] = "relogin"
        else:
            alerts["repassword"] = "repassword"


    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'form': login_lang["login"]["form"],
        'alert': alerts,
        'alerts': login_lang["login"]["long_texts"]["alerts"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'POST': request.POST,
        'important': UNIVERSAL_LANG["universal"]["important"],
        'forgot_password_info': login_lang["login"]["long_texts"]["forgot_password_info"]
    }

    return render(request, 'login/forgotpassword.html', args)
