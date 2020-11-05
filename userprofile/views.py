from django.shortcuts import render
# Create your views here.

from login.models import User
from tools.crypto import gen_rsa, secret_scrambler


from tools.confman import get_lang

UNIVERSAL_LANG = get_lang(sections=["universal"])
# Create your views here.

def ProfileView(request):
    profile_lang = get_lang(sections=["userprofile"])
    print(profile_lang.keys())
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'profile': profile_lang["userprofile"]["long_texts"]
    }

    return render(request, 'userprofile/profile.html', args)

def EditProfileView(request):
    profile_lang = get_lang(sections=["userprofile"])
    login_lang = get_lang(sections=["login"])
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'form': login_lang["login"]["form"],
        'profile': profile_lang["userprofile"]["long_texts"]
    }

    
    return render(request, 'userprofile/edit.html', args)
