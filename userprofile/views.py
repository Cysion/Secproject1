from django.shortcuts import render
# Create your views here.

from login.models import User
from tools.crypto import gen_rsa, secret_scrambler


from tools.confman import get_lang

UNIVERSAL_LANG = get_lang(sections=["universal"])
# Create your views here.

def ProfileView(request):
    login_lang = get_lang(sections=["userprofile"])
    print(login_lang.keys())
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'profile': login_lang["userprofile"]["long_texts"]
    }

    return render(request, 'userprofile/profile.html', args)
