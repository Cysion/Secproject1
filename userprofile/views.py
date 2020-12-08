from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.

from userprofile.models import RelationFrom, RelationTo
from login.models import User
from tools.crypto import gen_rsa, secret_scrambler
from tools.confman import get_lang
from tools.mediaman import reencrypt_user
from django.db import transaction
from prepare.views import reencryptMedia
from tools.crypto import gen_rsa, secret_scrambler, rsa_encrypt, rsa_decrypt, rsa_encrypt_long, rsa_decrypt_long

from science.views import new_entry

UNIVERSAL_LANG = get_lang(sections=["universal"])
# Create your views here.

def ProfileView(request):
    if 'UserId' not in request.session.keys():  # Check if user is logged in
        return HttpResponseRedirect(reverse('login:Login'))

    user1 = User.objects.filter(UserId=request.session['UserId'])[0]
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

    if request.session["Role"] == "User":
        template = "base.html"
    else:
        template = "base_professionals.html"

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

    profile_lang = get_lang(sections=["userprofile"])
    login_lang = get_lang(sections=["login"])

    wrong_pass = False
    account = {}
    user=User.objects.filter(UserId=request.session['UserId'])[0]
    account['firstName']=user.getFirstName(request.session['PrivKey'])
    account['lastName']=user.getLastName(request.session['PrivKey'])
    account['gender']=user.getGender(request.session['PrivKey'])
    account['email'] = user.getEmail()

    if request.method == 'POST':
        if checkPassword(request.session['UserId'], request.session['PrivKey'], request.POST['password']):
            user = User.objects.filter(UserId=request.session['UserId'])[0]
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
                "lastname":(account['lastName'], user.getLastNate(request.session['PrivKey'])),
                "gender":(account['gender'], user.getGender(request.session['PrivKey'])),
                "email":(account['email'], user.getEmail(request.session['PrivKey']))
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


    if request.session["Role"] == "User":
        template = "base.html"
    else:
        template = "base_professionals.html"

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'form': login_lang["login"]["form"],
        'profile': profile_lang["userprofile"]["long_texts"],
        'alerts': login_lang['login']['long_texts']['alerts'],
        "account":account,
        'wrong_pass':wrong_pass,
        'template': template,
        'profView': False
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

        if checkPassword(request.session['UserId'], request.session['PrivKey'], request.POST["current_password"]):
            if request.POST['new_password'] == request.POST['new_repassword']:
                PrivKey = changePass(request.session['UserId'], request.session['PrivKey'], request.POST["new_password"]).decode('utf-8')

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

    if request.session["Role"] == "User":
        template = "base.html"
    else:
        template = "base_professionals.html"

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


def changePass(uId:int, PrivKey, newPassword:str):
    user=User.objects.filter(UserId=uId)[0]
    firstName=user.getFirstName(PrivKey)
    lastName=user.getLastName(PrivKey)
    gender=user.getGender(PrivKey)
    dateOfBirth=user.getDateOfBirth(PrivKey)
    symKey=user.getSymKey(PrivKey)
    anonId = user.getAnonId(PrivKey)

    key = gen_rsa(secret_scrambler(newPassword, uId))
    pubkey=key.publickey().export_key()
    PrivKeyNew = key.export_key().decode("utf-8")
    with transaction.atomic():
        user.setPubKey(pubkey)
        user.setGender(gender)
        user.setFirstName(firstName.capitalize())
        user.setLastName(lastName.capitalize())
        user.setDateOfBirth(dateOfBirth)
        print(f"Symkey: {user.Symkey}")
        retVal = reencrypt_user(anonId, symKey)
        user.setSymkey(retVal[0])
        user.setAnonId(PrivKeyNew)
        user.save()

        reencryptMedia(user.getUid(), PrivKey, pubkey, retVal[1])

        relationsTo = RelationTo.objects.filter(UserIdFrom=user.getUid())
        for relation in relationsTo:
            reciever = User.objects.filter(UserId=relation.getUserIdToDecryptedFrom(PrivKey))[0]
            relation.setFromPrivEncrypted(reciever.getPubkey(), key.export_key().decode("utf-8"))
            relation.setUserIdToEncryptedFrom(pubkey, reciever.getUid())
            relation.save()

        return key.export_key()

    return 0

def checkPassword(uId:int, PrivKey, password:str):
    return gen_rsa(secret_scrambler(password, uId)).export_key().decode("utf-8") == PrivKey

def BackupKeyView(request):
    if not 'UserId' in request.session.keys():
        return HttpResponseRedirect(reverse('login:Login'))

    profile_lang = get_lang(sections=["userprofile"])

    if request.session["Role"] == "User":
        template = "base.html"
    else:
        template = "base_professionals.html"


    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'backup': profile_lang["userprofile"]["long_texts"]["backupkey"],
        'PrivKey': request.session['PrivKey'],
        'template': template
    }

    return render(request, 'userprofile/backupkey.html', args)

def relationsView(request):
    if not 'UserId' in request.session.keys():
        return HttpResponseRedirect(reverse('login:Login'))


    users = showAllRelationsTo(request.session['UserId'], request.session['PrivKey'])

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

    profile_lang = get_lang(sections=["userprofile"])

    alerts=dict()
    if request.method == 'POST':
        if User.objects.filter(Email=request.POST['email'].lower()):
            recieverEmail= request.POST['email'].lower()
        else:
            alerts['email'] = 'email_does_not_exist'

        if not alerts:
            user=User.objects.filter(UserId=request.session['UserId'])[0]
            permissions = '1'
            permissions+='1' if 'share_savemeplan' in request.POST else '0'
            permissions+='1' if 'share_check' in request.POST else '0'
            permissions+='1' if 'share_prepare' in request.POST else '0'
            permissions+='1' if 'share_media' in request.POST else '0'
            new_entry("r1", user.getAnonId(request.session['PrivKey']), "professional: " + permissions)

            if not createRelation(user.getUid(), request.session['PrivKey'], recieverEmail, permissions):
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
    profile_lang = get_lang(sections=["userprofile"])
    relationData = dict()
    if request.GET:
        relationFrom = RelationFrom.objects.filter(RelationFromId=request.GET['Id'])[0]
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
                removeRelation(request.session['UserId'], request.session['PrivKey'], email)
                return HttpResponseRedirect(reverse('userprofile:Relations'))
            elif 'save' in request.POST:
                relationFrom = RelationFrom.objects.filter(RelationFromId=request.GET['Id'])[0]
                permission['Profile'] = '1'
                permission['SaveMePlan'] ='1' if 'share_savemeplan' in request.POST else '0'
                permission['Check'] = '1' if 'share_check' in request.POST else '0'
                permission['Prepare'] = '1' if 'share_prepare' in request.POST else '0'
                permission['Media'] = '1' if 'share_media' in request.POST else '0'
                modifyRelation(request.session['UserId'], request.session['PrivKey'], email, permission)
                relationData['Permission']=permission




    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'relations': profile_lang["userprofile"]["relations"],
        'form': profile_lang["userprofile"]["relations"]["form"],
        'modal': profile_lang["userprofile"]["relations"]["modal"],
        'user': relationData
    }

    return render(request, 'userprofile/managerelations.html', args)

def createRelation(uId:int, PrivKey, recieverEmail:str, permissions:str):
    """Returns 1 if relation is added or 0 if it failed.
    permissions is a binary string containing 5 bits representing
    Profile
    SaveMePlan
    Check
    Prepare
    Media
    """
    user = User.objects.filter(UserId=uId)[0]
    reciever = User.objects.filter(Email=recieverEmail.lower())[0]

    #try:
    with transaction.atomic():
        relationFromEntry = RelationFrom(
            AnonymityIdFrom = user.getAnonId(PrivKey),
            UserIdTo = reciever,
            Permission = permissions,
            UserIdFromEncrypted = rsa_encrypt( reciever.getPubkey(), str(user.getUid()).encode("utf-8"))
        )
        relationFromEntry.save()
        print(reciever)
        relationToEntry = RelationTo(
            UserIdFrom = user,
            Permission = permissions,
            UserIdToEncryptedTo = rsa_encrypt(reciever.getPubkey(),str(reciever.getUid()).encode("utf-8")),
            UserIdToEncryptedFrom = rsa_encrypt(user.getPubkey(),str(reciever.getUid()).encode("utf-8")),
            FromPrivEncrypted = rsa_encrypt_long(reciever.getPubkey(), PrivKey.encode("utf-8"))
        )
        relationToEntry.save()
    #except: #Exeption as e: #Possible exceptions here
        #return 1
    #else:
    return 0

def updateRelationTo(recieverUId:int, recieverPrivKey):
    """Because a user sharing data cannot complete the RelationTo entry, it has to be updated by the reciever.
    Returns 1 on success, 0 on failure"""
    reciever = User.objects.filter(UserId=recieverUId)[0]
    relationsFrom = RelationFrom.objects.filter(UserIdTo=reciever)
    relationsToReciever = RelationTo.objects.filter(AnonymityIdTo=reciever.getAnonId(recieverPrivKey))
    if(len(relationsFrom) != len(relationsToReciever)):
        diff = abs(len(relationsFrom) - len(relationsToReciever))
        print(diff)
        for relationFrom in relationsFrom:
            relationFrom.getUserIdFromDecrypted(recieverPrivKey)
            relationsTo = RelationTo.objects.filter(UserIdFrom=User.objects.filter(UserId=relationFrom.getUserIdFromDecrypted(recieverPrivKey))[0])
            for relationTo in relationsTo:
                print(relationTo)
                try:
                    uIdTo = relationTo.getUserIdToDecryptedTo(recieverPrivKey)
                except ValueError:
                    pass
                else:
                    if uIdTo == reciever.getUid():
                        if relationTo.getAnonymityIdTo() != reciever.getAnonId(recieverPrivKey):
                            relationTo.setAnonymityIdTo(reciever.getAnonId(recieverPrivKey))
                            relationTo.save()
                            diff -= 1
                            if not diff:

                                return 1
        return 0
    else:
        return 1


def showAllRelationsTo(uId, PrivKey):
    """Returns the email address of everyone who the user shares data with"""
    user = User.objects.filter(UserId=uId)[0]
    relationsFrom = RelationFrom.objects.filter(AnonymityIdFrom=user.getAnonId(PrivKey))
    return [{'Email':relation.getUserIdTo().getEmail(), 'RelationFrom': relation.getRelationFromId()} for relation in relationsFrom]


def showAllRelationsFrom(recieverUId, recieverPrivKey):
    reciever = User.objects.filter(UserId=recieverUId)[0]
    relationsTo = RelationTo.objects.filter(AnonymityIdTo=reciever.getAnonId(recieverPrivKey))
    toReturn = []
    for relation in relationsTo:
        userDict = dict()
        userDict['FirstName'] = relation.getUserIdFrom().getFirstName(relation.getFromPrivDecrypted(recieverPrivKey).decode("utf-8"))
        userDict['LastName'] = relation.getUserIdFrom().getLastName(relation.getFromPrivDecrypted(recieverPrivKey).decode("utf-8"))
        userDict['UserId'] = relation.getUserIdFrom().getUid()
        permissions = dict()
        permissions['Profile'] = int(relation.getPermission()[0])
        permissions['SaveMePlan'] = int(relation.getPermission()[1])
        permissions['Check'] = int(relation.getPermission()[2])
        permissions['Prepare'] = int(relation.getPermission()[3])
        permissions['Media'] = int(relation.getPermission()[4])
        userDict['Permissions'] = permissions
        toReturn.append(userDict)
    return toReturn

def removeRelation(uId, PrivKey, recieverEmail):
    user = User.objects.filter(UserId=uId)[0]
    reciever = User.objects.filter(Email=recieverEmail.lower())[0]

    with transaction.atomic():
        RelationFrom.objects.filter(AnonymityIdFrom=user.getAnonId(PrivKey), UserIdTo=reciever.getUid()).delete()
        relationsTo = RelationTo.objects.filter(UserIdFrom=user)
        for relationTo in relationsTo:
            if relationTo.getUserIdToDecryptedFrom(PrivKey) == reciever.getUid():
                relationToId = relationTo.getRelationToId()
                relationsTo.filter(RelationToId=relationToId).delete()
        return 0
    return 1

def modifyRelation(uId, PrivKey, recieverEmail, permission):
    permissionString = '1'
    permissionString += permission['SaveMePlan']
    permissionString += permission['Check']
    permissionString += permission['Prepare']
    permissionString += permission['Media']

    user = User.objects.filter(UserId=uId)[0]
    reciever = User.objects.filter(Email=recieverEmail.lower())[0]
    with transaction.atomic():
        relationFrom=RelationFrom.objects.filter(AnonymityIdFrom=user.getAnonId(PrivKey), UserIdTo=reciever.getUid())[0]
        relationFrom.setPermission(permissionString)
        relationFrom.save()
        relationsTo = RelationTo.objects.filter(UserIdFrom=user)
        for relationTo in relationsTo:
            if relationTo.getUserIdToDecryptedFrom(PrivKey) == reciever.getUid():
                relationTo.setPermission(permissionString)
                relationTo.save()
        return 0
    return 1


def sharesDataWith(userId, recieverId, recieverPrivKey):
    reciever = User.objects.filter(UserId=recieverId)[0]
    relationTo = RelationTo.objects.filter(UserIdFrom=userId, AnonymityIdTo=reciever.getAnonId(recieverPrivKey))
    if relationTo:
        relationTo = relationTo[0]
        return relationTo.getFromPrivDecrypted(recieverPrivKey)
    else:
        return False
