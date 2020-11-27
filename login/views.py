from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.


from login.models import User
from django.db import transaction
from tools.crypto import gen_rsa, secret_scrambler, rsa_encrypt, rsa_decrypt
from userprofile.views import checkPassword, changePass

from tools.confman import get_lang

UNIVERSAL_LANG = get_lang(sections=["universal"])

def RegisterView(request):
    '''
    This view will display the registration page and when submitting a
    registration it will enter here.

    If submitting a registration POST will contain the following.
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

        login_lang = get_lang(sections=["login"])  # Get language text for form.
        # Check if a user have submitted a form.
        if request.method == 'POST':
            for index in ['first_name','last_name','gender','gender_other', 'email']:
                exceptions = ''
                if index == 'email':
                    exceptions = '1234567890@!#$%&*+-/=?^_`{|}~.'
                if containsBadChar(request.POST[index], exceptions):
                    alerts[index] = "badChar"

            if request.POST["password"] != request.POST["repassword"]:
                alerts['repassword'] = "repassword"
            if getUidFromEmail(request.POST["email"]):
                alerts['email'] = 'email_already_exists'
            if not alerts:
                try:
                    with transaction.atomic():
                        sessionsData = registerUser(request.POST)
                except AttributeError:
                    alerts['database'] = 'Database error'
                else:
                    request.session['UserId'] = sessionsData[0]
                    request.session['PrivKey'] = sessionsData[1].decode("utf-8")
                    request.session['Role'] = sessionsData[2]

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

def containsBadChar(stringToCheck:str, exceptions:str = ''):
    badChar = set("¨%\"5+1¶`<0½~¤9]&/*?6:.£7'2¡=8>|}#-´4[(±\@_{§)^€;!,¥$3").difference(set(exceptions))
    return True if set(stringToCheck).intersection(badChar) else False


def getUidFromEmail(newMail):
    user = User.objects.filter(Email=newMail).values('UserId')
    if user:
        return user[0]["UserId"]
    return False

def registerUser(postData): # Place function somewere else.
    user = User(Email=postData["email"].lower())
    user.save()
    key = gen_rsa(secret_scrambler(postData["password"], user.UserId))

    user.setPubKey(key.publickey().export_key())
    if postData['gender'] == 'Other':
        user.setGender(postData['gender_other'])
    else:
        user.setGender(postData['gender'])
    user.setFirstName(postData['first_name'])
    user.setLastName(postData['last_name'])
    user.setDateOfBirth(postData['date_of_birth'])
    user.setRole('professional') if 'professional' in postData else user.setRole('User')
    user.setAnonId(key.export_key().decode("utf-8"))
    user.setSymkey()
    user.save()
    return user.getUid(), key.export_key(), user.getRole()


def LoginView(request):
    if 'UserId' in request.session:
        return HttpResponseRedirect(reverse('userprofile:Profile'))

    loginFail = False
    if request.method == 'POST':
        try:
            user = User.objects.filter(Email=request.POST['email'].lower())[0]
        except Exception as e:
            user = None
            loginFail = True

        if user:
            key = gen_rsa(secret_scrambler(request.POST["password"], user.getUid()))
            if str(key.publickey().export_key()) == str(user.getPubkey()):
                request.session['UserId'] = user.getUid()
                request.session['PrivKey'] = key.export_key().decode("utf-8")
                request.session['Role'] = user.getRole()

                return HttpResponseRedirect(reverse('userprofile:Profile'))
            else:
                loginFail = True
        else:
            loginFail = True

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    login_lang = get_lang(sections=["login"])
    args = {
        'post': request.POST,
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'form': login_lang["login"]["form"],
        'alerts': login_lang['login']['long_texts']['alerts'],
        'wrong_login_enterd': loginFail  # A check if right login was entered
    }

    return render(request, 'login/login.html', args)


def forgotPasswordView(request):
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
                user = User.objects.filter(Email=request.POST['email'])[0]
            except Exception as e:
                user = None
            if user:
                try:
                    request.session['UserId'] = user.getUid()
                    request.session['PrivKey']=changePass(user.UserId, request.POST['priv_key'], request.POST['password']).decode("utf-8")
                except ValueError as keyError:
                    alerts["relogin"] = "relogin"

                    alert = {
                        "color": "success",  # Check https://www.w3schools.com/bootstrap4/bootstrap_alerts.asp for colors.
                        "title": UNIVERSAL_LANG["universal"]["success"],  # Should mostly be success, error or warning. This text is the bold text.
                        "message": profile_lang["login"]["long_texts"]["alerts"]["changed_password_success"]
                    }

                if "global_alerts" not in request.session.keys():  # Check if global_elerts is in session allready.
                    request.session["global_alerts"] = [alert]
                else:
                    request.session["global_alerts"].append(alert)

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
