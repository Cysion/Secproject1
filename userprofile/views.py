from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

import userprofile.models
import login.models
from tools.confman import get_lang
import tools.mediaman
from django.db import transaction
from science.tools import new_entry, forget_me, gdpr_csv
import userprofile.tools
from prepare.tools import delete_temp_files

UNIVERSAL_LANG = get_lang(sections=["universal"])

def profile_view(request):
    """Main profile view for a user. Used by users and professionals.
    """
    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    user = login.models.User.objects.filter(UserId=request.session['UserId'])[0]
    if request.method == 'GET':  # Used for logout. logout is in GET keys with a value of 1.
        if 'logout' in request.GET.keys():
            new_entry("u2", user.getAnonId(request.session['PrivKey']), "na", role=request.session['Role'])
            request.session.flush()
            return HttpResponseRedirect(reverse('login:Login'))

    profile_lang = get_lang(sections=["userprofile"])
    login_lang = get_lang(sections=["login"])
    new_entry("g1", user.getAnonId(request.session['PrivKey']), "prof", role=request.session['Role'])
    first_name = user.getFirstName(request.session['PrivKey'])
    last_name = user.getLastName(request.session['PrivKey'])

    global_alerts = []  # The variable which is sent to template

    if "global_alerts" in request.session.keys():  # Check if global_elerts is in session allready.
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    template = "base_professionals.html" if request.session["Role"] == "Professional" else "base.html"
    profView = True if request.session["Role"] == "Professional" else False

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'global_alerts': global_alerts,
        'form': login_lang["login"]["form"],
        'userprofile':profile_lang["userprofile"],
        'profile': profile_lang["userprofile"]["long_texts"],
        'first_name': first_name,
        'last_name': last_name,
        'template': template,
        'profView' : profView
    }

    return render(request, 'userprofile/profile.html', args)

def edit_profile_view(request):
    """Used to edit user data.
    If submitting a change request.POST will contain the following keys:
        first_name - Users first name
        last_name - Users last name
        gender - Gender of the user. Is one of the following
            Male
            Female
            Other
        gender_other - If user choose gender=Other this will contain a text.
        email - Users email.
        password - Users entered non hashed password, will be checked and needs to be correct for change to be done.
    request.GET is used for deletion of the entire account.
    """
    if not 'UserId' in request.session.keys():
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    profile_lang = get_lang(sections=["userprofile"])
    login_lang = get_lang(sections=["login"])

    wrong_pass = False
    account = {}
    user=login.models.User.objects.filter(UserId=request.session['UserId'])[0]
    account['firstName']=user.getFirstName(request.session['PrivKey'])
    account['lastName']=user.getLastName(request.session['PrivKey'])
    account['gender']=user.getGender(request.session['PrivKey'])
    account['email'] = user.getEmail()

    if request.GET:
        if request.GET['delete']:
            if userprofile.tools.check_password(request.session['UserId'], request.session['PrivKey'], request.POST['password']):
                if request.POST['password']:
                    user = login.models.User.objects.filter(UserId=request.session['UserId'])[0]
                    with transaction.atomic():
                        if not 'researchData' in request.POST.keys():
                            forget_me(user.getAnonId(request.session['PrivKey']))
                        if request.session['Role'] == 'User':
                            userprofile.tools.remove_all_of_users_relations(request.session['UserId'], request.session['PrivKey'])
                        elif request.session['Role'] == 'Professional':
                            userprofile.tools.remove_all_of_professionals_relations(request.session['UserId'], request.session['PrivKey'])
                        tools.mediaman.delete_all_files(user.getAnonId(request.session['PrivKey']))
                        login.models.User.objects.filter(UserId=request.session['UserId']).delete()
                        request.session.flush()
                    return HttpResponseRedirect(reverse('login:Login'))
            else:
                return HttpResponseRedirect(reverse('userprofile:Edit-profile'))
    if request.method == 'POST':
        if userprofile.tools.check_password(request.session['UserId'], request.session['PrivKey'], request.POST['password']):
            user = login.models.User.objects.filter(UserId=request.session['UserId'])[0]
            if request.POST['gender'] == 'Other':
                user.setGender(request.POST['gender_other'])
            else:
                user.setGender(request.POST['gender'])
            user.setFirstName(request.POST['first_name'])
            user.setLastName(request.POST['last_name'])
            user.setEmail(request.POST['email'])
            user.save()

            #data collection
            for_science = {
                "firstname":(account['firstName'] ,user.getFirstName(request.session['PrivKey'])),
                "lastname":(account['lastName'], user.getLastName(request.session['PrivKey'])),
                "gender":(account['gender'], user.getGender(request.session['PrivKey'])),
                "email":(account['email'], user.getEmail())
            }
            for science in for_science:
                if for_science[science][0] != for_science[science][0]:
                    new_entry("u3", user.getAnonId(request.session['PrivKey']), science, role=request.session['Role'])
            del for_science, science

            alert = {
                "color": "success",
                "title": UNIVERSAL_LANG["universal"]["success"],  # Should mostly be success, error or warning. This text is the bold text.
                "message": profile_lang["userprofile"]["long_texts"]["alerts"]["changed_info_success"]
            }

            # Check if global_elerts is in session allready.
            if "global_alerts" not in request.session.keys():
                request.session["global_alerts"] = [alert]
            else:
                request.session["global_alerts"].append(alert)
            return HttpResponseRedirect(reverse('userprofile:Profile'))
        else:
            wrong_pass = True

    template = "base_professionals.html" if request.session["Role"] == "Professional" else "base.html"

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'form': login_lang["login"]["form"],
        'userprofile': profile_lang["userprofile"],
        'profile': profile_lang["userprofile"]["long_texts"],
        'alerts': login_lang['login']['long_texts']['alerts'],
        "account":account,
        'wrong_pass':wrong_pass,
        'template': template,
        'profView': False
    }

    return render(request, 'userprofile/edit.html', args)

def backup_key_view(request):
    """Used to display a users private key used to restore the account and reset the password in case the password is forgotten.
    Requires a correct password in request.POST
    """

    if not 'UserId' in request.session.keys():
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    profile_lang = get_lang(sections=["userprofile"])
    template = "base_professionals.html" if request.session["Role"] == "Professional" else "base.html"
    privkey = ''

    if request.method == 'POST':
        if userprofile.tools.check_password(request.session['UserId'], request.session['PrivKey'], request.POST['password']):
            privkey = request.session['PrivKey']
        else:
            privkey = profile_lang["userprofile"]["long_texts"]["wrongpass"]

    elif "seen_backup" in request.session:
        if not request.session["seen_backup"]:
            request.session["seen_backup"] = 1
            privkey = request.session['PrivKey']

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'backup': profile_lang["userprofile"]["long_texts"]["backupkey"],
        'template': template,
        'PrivKey' : privkey
    }

    return render(request, 'userprofile/backupkey.html', args)


def change_pass_view(request):
    """
    A interface for changing password.

    If submitting a request to change password, request.POST will contain the following keys:
        current_password = Users current password. Used for verification.
        new_password = Users new password.
        new_repassword = Users new password reentered.
    """

    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    alerts = {}  # Dict containing input name as key and alert text key as value
    login_lang = get_lang(sections=["login"])
    profile_lang = get_lang(sections=["userprofile"])

    if request.method == "POST":
        if userprofile.tools.check_password(request.session['UserId'], request.session['PrivKey'], request.POST["current_password"]):
            if request.POST['new_password'] == request.POST['new_repassword']:
                if len(request.POST["new_password"]) > 5 and len(request.POST["new_password"]) < 129:
                    PrivKey = userprofile.tools.change_pass(request.session['UserId'], request.session['PrivKey'], request.POST["new_password"],request.session['Role']).decode('utf-8')

                    if PrivKey:  # Check if changing password succeded
                        request.session['PrivKey'] = PrivKey
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
                else:
                    alerts["password"] = 'bad_length'
            else:  # new_password and new_repasswords are not the same
                alerts["repassword"] = "repassword"
        else:  # current_password is not the right one
            alerts["current_password"] = "relogin"

    global_alerts = []
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]
        request.session["global_alerts"] = []

    template = "base_professionals.html" if request.session["Role"] == "Professional" else "base.html"

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'global_alerts': global_alerts,
        'change_password_text': profile_lang["userprofile"]["long_texts"]["change_password_text"],
        'form': login_lang["login"]["form"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'alerts': login_lang['login']['long_texts']['alerts'],
        'alert': alerts,
        'important': UNIVERSAL_LANG["universal"]["important"],
        'template': template
    }

    return render(request, 'userprofile/changepassword.html', args)


def relations_view(request):
    """Displays all of a users relations (who the user is sharing data with)
    """

    if not 'UserId' in request.session.keys():
        return HttpResponseRedirect(reverse('login:Login'))
    elif request.session["Role"] != "User":
        return HttpResponseRedirect(reverse('userprofile:Profile'))
    if request.session["Role"] != "User":
        return HttpResponseRedirect(reverse('userprofile:Profile'))

    delete_temp_files(request.session)
    users = userprofile.tools.show_all_relations_to(request.session['UserId'], request.session['PrivKey'])
    profile_lang = get_lang(sections=["userprofile"])
    template = "base.html"
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'relations': profile_lang["userprofile"]["relations"],
        'template' : template,
        'users': users
    }

    return render(request, 'userprofile/relations.html', args)


def add_relations_view(request):
    """Used to add a new relation.

    If submitting a request to add a relation, request.POST will contain the following keys:
        email = Email address of the reciever
        share_savemeplan = 1 if savemeplan should be shared, else 0
        share_check = 1 if check should be shared, else 0
        share_prepare = 1 if prepare should be shared, else 0
        share_media = 1 if media should be shared, else 0
    """
    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))
    elif request.session["Role"] != "User":
        return HttpResponseRedirect(reverse('userprofile:Profile'))

    delete_temp_files(request.session)

    profile_lang = get_lang(sections=["userprofile"])

    alerts=dict()
    if request.method == 'POST':
        if login.models.User.objects.filter(Email=request.POST['email'].lower()):
            recieverEmail= request.POST['email'].lower()
            reciever = login.models.User.objects.filter(Email=recieverEmail)[0]
            if reciever.getRole() != 'Professional':
                alerts['email'] = 'email_does_not_exist'
        else:
            alerts['email'] = 'email_does_not_exist'

        if not alerts:
            user=login.models.User.objects.filter(UserId=request.session['UserId'])[0]
            permissions = '1'
            permissions+='1' if 'share_savemeplan' in request.POST else '0'
            permissions+='1' if 'share_check' in request.POST else '0'
            permissions+='1' if 'share_prepare' in request.POST else '0'
            permissions+='1' if 'share_media' in request.POST else '0'
            new_entry("r1", user.getAnonId(request.session['PrivKey']), "professional: " + permissions, role=request.session['Role'])

            if not userprofile.tools.create_relation(user.getUid(), request.session['PrivKey'], recieverEmail, permissions):
                return HttpResponseRedirect(reverse('userprofile:Relations'))
            else:
                alerts['database'] = 'database_error'

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'relations': profile_lang["userprofile"]["relations"],
        'form': profile_lang["userprofile"]["relations"]["form"],
        'alerts': alerts,
        "alert": profile_lang["userprofile"]["long_texts"]["alerts"],
        "warning": UNIVERSAL_LANG["universal"]["warning"]
    }
    return render(request, 'userprofile/addrelations.html', args)


def manage_relations_view(request):
    """Used to change permissions in a relation
    If submitting a request to change a relation, request.POST will contain the following keys:
        share_savemeplan = 1 if savemeplan should be shared, else 0
        share_check = 1 if check should be shared, else 0
        share_prepare = 1 if prepare should be shared, else 0
        share_media = 1 if media should be shared, else 0

    request.GET is used to send RelationFromId
        """

    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))
    elif request.session["Role"] != "User":
        return HttpResponseRedirect(reverse('userprofile:Profile'))

    delete_temp_files(request.session)

    profile_lang = get_lang(sections=["userprofile"])
    relationData = dict()
    if request.GET:
        relationFrom = userprofile.models.RelationFrom.objects.filter(RelationFromId=request.GET['Id'])[0]
        permission = dict()
        user = relationFrom.getUserIdTo()
        email = user.getEmail()
        permission['Profile'] = int(relationFrom.getPermission()[0])
        permission['SaveMePlan'] = int(relationFrom.getPermission()[1])
        permission['Check'] = int(relationFrom.getPermission()[2])
        permission['Prepare'] = int(relationFrom.getPermission()[3])
        permission['Media'] = int(relationFrom.getPermission()[4])
        relationData = {'Email':email, 'RelationFrom':request.GET['Id'], 'Permission':permission}

        if request.method == 'POST':
            if 'delete' in request.POST:
                userprofile.tools.remove_relation(request.session['UserId'], request.session['PrivKey'], email)
                return HttpResponseRedirect(reverse('userprofile:Relations'))
            elif 'save' in request.POST:
                relationFrom = userprofile.models.RelationFrom.objects.filter(RelationFromId=request.GET['Id'])[0]
                permission['Profile'] = 1
                permission['SaveMePlan'] = 1 if 'share_savemeplan' in request.POST else 0
                permission['Check'] = 1 if 'share_check' in request.POST else 0
                permission['Prepare'] = 1 if 'share_prepare' in request.POST else 0
                permission['Media'] = 1 if 'share_media' in request.POST else 0
                userprofile.tools.modify_relation(request.session['UserId'], request.session['PrivKey'], email, permission)
                relationData['Permission']=permission

    print(relationData['Permission'])
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'relations': profile_lang["userprofile"]["relations"],
        'form': profile_lang["userprofile"]["relations"]["form"],
        'modal': profile_lang["userprofile"]["relations"]["modal"],
        'user': relationData
    }

    return render(request, 'userprofile/managerelations.html', args)


def gdpr_view(request):
    """Used to display options regarding handling of user data and research data.
    """

    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)
    profile_lang = get_lang(sections=["userprofile"])
    login_lang = get_lang(sections=["login"])

    template = "base_professionals.html" if request.session["Role"] == "Professional" else "base.html"

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'userprofile': profile_lang["userprofile"],
        'form': login_lang["login"]["form"],
        'template': template
    }

    return render(request, 'userprofile/gdpr.html', args)


def research_data_view(request):
    """Used to display all research data that has been collected on a user.

    request.GET is used for deletion of a relation.
    """

    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)
    profile_lang = get_lang(sections=["userprofile"])

    template = "base_professionals.html" if request.session["Role"] == "Professional" else "base.html"

    if request.GET:
        print(request.GET)
        if 'cleared' in request.GET.keys():
            print(request.GET['cleared'])
            if request.GET['cleared'] == 'true':
                user=login.models.User.objects.filter(UserId=request.session['UserId'])[0]
                forget_me(user.getAnonId(request.session['PrivKey']))

    user = login.models.User.objects.filter(UserId=request.session["UserId"])[0]
    text = gdpr_csv(user.getAnonId(request.session['PrivKey']))

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'userprofile': profile_lang["userprofile"],
        'template': template,
        'text': text
    }

    return render(request, 'userprofile/researchdata.html', args)
