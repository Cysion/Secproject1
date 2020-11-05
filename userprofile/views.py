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
    if not 'UserId' in request.session.keys():
        return HttpResponseRedirect(reverse('login:Login'))

    if request.method == 'GET':
        if 'logout' in request.GET.keys():
            request.session.flush()
            return HttpResponseRedirect(reverse('login:Login'))

    login_lang = get_lang(sections=["userprofile"])
    user1=User.objects.filter(UserId=request.session['UserId'])[0]
    first_name=user1.getFirstName(request.session['privKey'])
    last_name=user1.getLastName(request.session['privKey'])

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'profile': login_lang["userprofile"]["long_texts"],
        'first_name': first_name,
        'last_name': last_name
    }

    return render(request, 'userprofile/profile.html', args)

def EditProfileView(request):
    user1=User.objects.filter(UserId=request.session['UserId'])[0]
    firstName=user1.getFirstName(request.session['privKey'])
    lastName=user1.getLastName(request.session['privKey'])
    dateOfBirth=user1.getDateOfBirth(request.session['privKey'])
    gender=user1.getGender(request.session['privKey'])
    email = user1.getEmail()

    account = {
        "firstName":firstName,
        "lastName":lastName,
        "dateOfBirth":dateOfBirth,
        "gender":gender,
        "email":email

    }

    profile_lang = get_lang(sections=["userprofile"])
    login_lang = get_lang(sections=["login"])
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'form': login_lang["login"]["form"],
        'profile': profile_lang["userprofile"]["long_texts"],
        "account":account
    }

    return render(request, 'userprofile/edit.html', args)

def changePassView(request):
    profile_lang = get_lang(sections=["userprofile"])
    login_lang = get_lang(sections=["login"])
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'form': login_lang["login"]["form"],
        'profile': profile_lang["userprofile"]["long_texts"]
    }


    return render(request, 'userprofile/edit.html', args)

def changePass(uId, privKey, newPassword):
    user1=User.objects.filter(UserId=uId)[0]
    firstName=user1.getFirstName(privKey)
    lastName=user1.getLastName(privKey)
    gender=user1.getGender(privKey)
    dateOfBirth=user1.getdateOfBirth(privKey)
    symKey=user1.getSymKey(privKey)
    
    key = gen_rsa(secret_scrambler(newPassword, uId))
    pubkey=key.publickey().export_key()
    with transaction.atomic():
        user1.Pubkey = pubkey
        user1.Gender=rsa_encrypt(pubkey, gender.encode("utf-8"))
        user1.FirstName=rsa_encrypt(pubkey, firstName.capitalize().encode("utf-8"))
        user1.LastName=rsa_encrypt(pubkey, lastName.capitalize().encode("utf-8"))
        user1.DateOfBirth=rsa_encrypt(pubkey, dateOfBirth.encode("utf-8"))
        user1.save()
        return key.export_key()

    return 0

