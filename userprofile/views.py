from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.

from login.models import User
from tools.crypto import gen_rsa, secret_scrambler
from tools.confman import get_lang
from django.db import transaction
from tools.crypto import gen_rsa, secret_scrambler, rsa_encrypt, rsa_decrypt

UNIVERSAL_LANG = get_lang(sections=["universal"])
# Create your views here.

def ProfileView(request):
    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))

    if request.method == 'GET':  # Used for logout. logout is in GET keys with a value of 1.
        if 'logout' in request.GET.keys():
            request.session.flush()
            return HttpResponseRedirect(reverse('login:Login'))

    login_lang = get_lang(sections=["userprofile"])
    user1 = User.objects.filter(UserId=request.session['UserId'])[0]
    first_name = user1.getFirstName(request.session['privKey'])
    last_name = user1.getLastName(request.session['privKey'])

    global_alerts = []  # The variable which is sent to template

    if "global_alerts" in request.session.keys():  # Check if global_elerts is in session allready.
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'global_alerts': global_alerts,
        'profile': login_lang["userprofile"]["long_texts"],
        'first_name': first_name,
        'last_name': last_name
    }

    return render(request, 'userprofile/profile.html', args)

def EditProfileView(request):
    if not 'UserId' in request.session.keys():
        return HttpResponseRedirect(reverse('login:Login'))
    wrong_pass = False
    account = {}
    user=User.objects.filter(UserId=request.session['UserId'])[0]
    account['firstName']=user.getFirstName(request.session['privKey'])
    account['lastName']=user.getLastName(request.session['privKey'])
    account['gender']=user.getGender(request.session['privKey'])
    account['email'] = user.getEmail()
    print(account['gender'])

    if request.method == 'POST':
        if checkPassword(request.session['UserId'], request.session['privKey'], request.POST['password']):
            user = User.objects.filter(UserId=request.session['UserId'])[0]
            if request.POST['gender'] == 'Other':
                user.setGender(request.POST['gender_other'])
            else:
                user.setGender(request.POST['gender'])
            user.setFirstName(request.POST['first_name'])
            user.setLastName(request.POST['last_name'])
            user.setEmail(request.POST['email'])
            user.save()
            return HttpResponseRedirect(reverse('userprofile:Profile'))
        else:
            wrong_pass = True




    profile_lang = get_lang(sections=["userprofile"])
    login_lang = get_lang(sections=["login"])
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'form': login_lang["login"]["form"],
        'profile': profile_lang["userprofile"]["long_texts"],
        'alerts': login_lang['login']['long_texts']['alerts'],
        "account":account,
        'wrong_pass':wrong_pass
    }

    return render(request, 'userprofile/edit.html', args)

def changePassView(request):
    """
    A interface for changeing password.

    Post variables:
        current_password = Users current password. Used for verification.
        new_password = Users new password.
        new_repassword = Users new password reentered.
    """

    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))

    alerts = {}  # Dict containing input name as key and alert text key as value
    login_lang = get_lang(sections=["login"])
    profile_lang = get_lang(sections=["userprofile"])

    if request.method == "POST":

        if checkPassword(request.session['UserId'], request.session['privKey'], request.POST["current_password"]):
            if request.POST['new_password'] == request.POST['new_repassword']:
                privkey = changePass(request.session['UserId'], request.session['privKey'], request.POST["new_password"]).decode('utf-8')

                if privkey:  # Check if changing password succeded
                    request.session['privKey'] = privkey
                    alert = {
                        "color": "success",
                        "title": UNIVERSAL_LANG["universal"]["success"],
                        "message": profile_lang["userprofile"]["long_texts"]["alerts"]["alert_changed_password"]
                    }

                    if "global_alerts" not in request.session.keys():
                        request.session["global_alerts"] = [alert]
                    else:
                        request.session["global_alerts"].append(alert)
                    return HttpResponseRedirect(reverse('userprofile:Profile'))

                else:  # Password change failed
                    alert = {
                        "color": "danger",
                        "title": UNIVERSAL_LANG["universal"]["error"],
                        "message": profile_lang["userprofile"]["long_texts"]["alert_error"]
                    }

                    if "global_alerts" not in request.session.keys():
                        alert = {
                            "color": "success",
                            "title": UNIVERSAL_LANG["universal"]["success"],
                            "message": profile_lang["userprofile"]["long_texts"]["alert_changed_password"]
                        }
                        request.session["global_alerts"] = [alert]
                    else:
                        request.session["global_alerts"].append(alert)

            else:  # new_password and new_repasswords are not the same
                alerts["repassword"] = "repassword"
        else:  # current_password is not the right one
            alerts["current_password"] = "relogin"

    global_alerts = []
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]
        request.session["global_alerts"] = []

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'global_alerts': global_alerts,
        'change_password_text': profile_lang["userprofile"]["long_texts"]["change_password_text"],
        'form': login_lang["login"]["form"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'alerts': login_lang['login']['long_texts']['alerts'],
        'alert': alerts
    }

    return render(request, 'userprofile/changepassword.html', args)


def changePass(uId, privKey, newPassword):
    user1=User.objects.filter(UserId=uId)[0]
    firstName=user1.getFirstName(privKey)
    lastName=user1.getLastName(privKey)
    gender=user1.getGender(privKey)
    dateOfBirth=user1.getDateOfBirth(privKey)
    symKey=user1.getSymKey(privKey)

    key = gen_rsa(secret_scrambler(newPassword, uId))
    pubkey=key.publickey().export_key()
    with transaction.atomic():
        user1.setPubKey(pubkey)
        user1.Gender=rsa_encrypt(pubkey, gender.encode("utf-8"))
        user1.FirstName=rsa_encrypt(pubkey, firstName.capitalize().encode("utf-8"))
        user1.LastName=rsa_encrypt(pubkey, lastName.capitalize().encode("utf-8"))
        user1.DateOfBirth=rsa_encrypt(pubkey, dateOfBirth.encode("utf-8"))
        user1.save()
        return key.export_key()

    return 0

def checkPassword(uId, privKey, password):
    return gen_rsa(secret_scrambler(password, uId)).export_key().decode("utf-8") == privKey

def BackupKeyView(request):
    if not 'UserId' in request.session.keys():
        return HttpResponseRedirect(reverse('login:Login'))

    profile_lang = get_lang(sections=["userprofile"])

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'backup': profile_lang["userprofile"]["long_texts"]["backupkey"],
        'privkey': request.session['privKey']
    }

    return render(request, 'userprofile/backupkey.html', args)

def relationsView(request):
    testuser0 = {
        'FirstName': 'Ludwig',
        'LastName': 'Wideskar',
        'Role': 'User'
    }
    testuser1 = {
        'FirstName': 'Kevin',
        'LastName': 'Engstrom',
        'Role': 'Professional'
    }
    testuser2 = {
        'FirstName': 'Joakim',
        'LastName': 'Karlsson',
        'Role': 'Admin'
    }
    #profile_lang = get_lang(sections=["userprofile"])
    login_lang = get_lang(sections=["login"])
    profile_lang = get_lang(sections=["userprofile"])
    
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'relations': profile_lang["userprofile"]["relations"],
        #'profile': profile_lang,
        'testuser0': testuser0,
        'testuser1': testuser1,
        'testuser2': testuser2
    }


    return render(request, 'userprofile/relations.html', args)

def addRelationsView(request):
    profile_lang = get_lang(sections=["userprofile"])

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'relations': profile_lang["userprofile"]["relations"],
        'form': profile_lang["userprofile"]["relations"]["form"]
    }

    return render(request, 'userprofile/addrelations.html', args)

def manageRelationsView(request):
    return render(request, 'userprofile/managerelations.html')