from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.

import userprofile.models
import login.models
from tools.confman import get_lang
import tools.mediaman
from django.db import transaction
from science.tools import new_entry, forget_me, gdpr_csv
import userprofile.tools
from prepare.tools import delete_temp_files
UNIVERSAL_LANG = get_lang(sections=["universal"])
# Create your views here.

def ProfileView(request):
    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    user1 = login.models.User.objects.filter(UserId=request.session['UserId'])[0]
    if request.method == 'GET':  # Used for logout. logout is in GET keys with a value of 1.
        if 'logout' in request.GET.keys():
            new_entry("u2", user1.getAnonId(request.session['PrivKey']), "na")
            request.session.flush()
            return HttpResponseRedirect(reverse('login:Login'))
    login_lang = get_lang(sections=["userprofile"])
    new_entry("g1", user1.getAnonId(request.session['PrivKey']), "prof")
    first_name = user1.getFirstName(request.session['PrivKey'])
    last_name = user1.getLastName(request.session['PrivKey'])

    global_alerts = []  # The variable which is sent to template

    if "global_alerts" in request.session.keys():  # Check if global_elerts is in session allready.
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    template = "base.html" if request.session["Role"] == "User" else "base_professionals.html"

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'global_alerts': global_alerts,
        'profile': login_lang["userprofile"]["long_texts"],
        'first_name': first_name,
        'last_name': last_name,
        'template': template
    }

    return render(request, 'userprofile/profile.html', args)

def EditProfileView(request):
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
            if userprofile.tools.checkPassword(request.session['UserId'], request.session['PrivKey'], request.POST['password']):
                if request.POST['password']:
                    user = login.models.User.objects.filter(UserId=request.session['UserId'])[0]
                    with transaction.atomic():
                        if not 'researchData' in request.POST.keys():
                            forget_me(user.getAnonId(request.session['PrivKey']))
                        if request.session['Role'] == 'User':
                            userprofile.tools.removeAllOfUsersRelations(request.session['UserId'], request.session['PrivKey'])
                        elif request.session['Role'] == 'Professional':
                            userprofile.tools.removeAllOfProfessionalsRelations(request.session['UserId'], request.session['PrivKey'])
                        tools.mediaman.delete_all_files(user.getAnonId(request.session['PrivKey']))
                        login.models.User.objects.filter(UserId=request.session['UserId']).delete()
                        request.session.flush()
                    return HttpResponseRedirect(reverse('login:Login'))
            else:
                return HttpResponseRedirect(reverse('userprofile:Edit-profile'))
    if request.method == 'POST':
        if userprofile.tools.checkPassword(request.session['UserId'], request.session['PrivKey'], request.POST['password']):
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
                    new_entry("u3", user.getAnonId(request.session['PrivKey']), science)
            del for_science, science


            alert = {
                "color": "success",  # Check https://www.w3schools.com/bootstrap4/bootstrap_alerts.asp for colors.
                "title": UNIVERSAL_LANG["universal"]["success"],  # Should mostly be success, error or warning. This text is the bold text.
                "message": profile_lang["userprofile"]["long_texts"]["alerts"]["changed_info_success"]
            }

            if "global_alerts" not in request.session.keys():  # Check if global_elerts is in session allready.
                request.session["global_alerts"] = [alert]
            else:
                request.session["global_alerts"].append(alert)
            return HttpResponseRedirect(reverse('userprofile:Profile'))
        else:
            wrong_pass = True


    template = "base.html" if request.session["Role"] == "User" else "base_professionals.html"

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

def BackupKeyView(request):
    if not 'UserId' in request.session.keys():
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    profile_lang = get_lang(sections=["userprofile"])

    template = "base.html" if request.session["Role"] == "User" else "base_professionals.html"


    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'backup': profile_lang["userprofile"]["long_texts"]["backupkey"],
        'PrivKey': request.session['PrivKey'],
        'template': template
    }

    return render(request, 'userprofile/backupkey.html', args)

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

    delete_temp_files(request.session)

    alerts = {}  # Dict containing input name as key and alert text key as value
    login_lang = get_lang(sections=["login"])
    profile_lang = get_lang(sections=["userprofile"])

    if request.method == "POST":

        if userprofile.tools.checkPassword(request.session['UserId'], request.session['PrivKey'], request.POST["current_password"]):
            if request.POST['new_password'] == request.POST['new_repassword']:
                PrivKey = userprofile.tools.changePass(request.session['UserId'], request.session['PrivKey'], request.POST["new_password"]).decode('utf-8')

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

            else:  # new_password and new_repasswords are not the same
                alerts["repassword"] = "repassword"
        else:  # current_password is not the right one
            alerts["current_password"] = "relogin"

    global_alerts = []
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]
        request.session["global_alerts"] = []

    template = "base.html" if request.session["Role"] == "User" else "base_professionals.html"

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



def relationsView(request):
    if not 'UserId' in request.session.keys():
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    users = userprofile.tools.showAllRelationsTo(request.session['UserId'], request.session['PrivKey'])

    profile_lang = get_lang(sections=["userprofile"])

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'relations': profile_lang["userprofile"]["relations"],
        'users': users
    }

    return render(request, 'userprofile/relations.html', args)

def addRelationsView(request):
    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)

    profile_lang = get_lang(sections=["userprofile"])

    alerts=dict()
    if request.method == 'POST':
        if login.models.User.objects.filter(Email=request.POST['email'].lower()):
            recieverEmail= request.POST['email'].lower()
        else:
            alerts['email'] = 'email_does_not_exist'

        if not alerts:
            user=login.models.User.objects.filter(UserId=request.session['UserId'])[0]
            permissions = '1'
            permissions+='1' if 'share_savemeplan' in request.POST else '0'
            permissions+='1' if 'share_check' in request.POST else '0'
            permissions+='1' if 'share_prepare' in request.POST else '0'
            permissions+='1' if 'share_media' in request.POST else '0'
            new_entry("r1", user.getAnonId(request.session['PrivKey']), "professional: " + permissions)

            if not userprofile.tools.createRelation(user.getUid(), request.session['PrivKey'], recieverEmail, permissions):
                return HttpResponseRedirect(reverse('userprofile:Relations'))
            else:
                alerts['database'] = 'database_error'


    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'relations': profile_lang["userprofile"]["relations"],
        'form': profile_lang["userprofile"]["relations"]["form"],
        'alerts': alerts
    }
    return render(request, 'userprofile/addrelations.html', args)

def manageRelationsView(request):
    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))

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
                userprofile.tools.removeRelation(request.session['UserId'], request.session['PrivKey'], email)
                return HttpResponseRedirect(reverse('userprofile:Relations'))
            elif 'save' in request.POST:
                relationFrom = userprofile.models.RelationFrom.objects.filter(RelationFromId=request.GET['Id'])[0]
                permission['Profile'] = 1
                permission['SaveMePlan'] = 1 if 'share_savemeplan' in request.POST else 0
                permission['Check'] = 1 if 'share_check' in request.POST else 0
                permission['Prepare'] = 1 if 'share_prepare' in request.POST else 0
                permission['Media'] = 1 if 'share_media' in request.POST else 0
                userprofile.tools.modifyRelation(request.session['UserId'], request.session['PrivKey'], email, permission)
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


def gdprView(request):
    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)
    profile_lang = get_lang(sections=["userprofile"])

    template = "base.html" if request.session["Role"] == "User" else "base_professionals.html"

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'userprofile': profile_lang["userprofile"],
        'template': template
    }

    return render(request, 'userprofile/gdpr.html', args)


def researchDataView(request):
    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))

    delete_temp_files(request.session)
    profile_lang = get_lang(sections=["userprofile"])

    template = "base.html" if request.session["Role"] == "User" else "base_professionals.html"

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
        'template': template,
        'text': text
    }

    return render(request, 'userprofile/researchdata.html', args)