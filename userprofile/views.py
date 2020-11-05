from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.

from login.models import User
from tools.crypto import gen_rsa, secret_scrambler


from tools.confman import get_lang

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

    account = {
        "firstName":firstName,
        "lastName":lastName,
        "dateOfBirth":dateOfBirth,
        "gender":gender
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
