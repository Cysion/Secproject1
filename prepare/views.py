from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.


from login.models import User
#from django.db import transaction
#from tools.crypto import gen_rsa, secret_scrambler, rsa_encrypt, rsa_decrypt
#from userprofile.views import checkPassword, changePass

from tools.confman import get_lang

UNIVERSAL_LANG = get_lang(sections=["universal"])

def MenuView(request):
    prepare_lang = get_lang(sections=["prepare"])
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'prepare': prepare_lang["prepare"]
    }
    return render(request, 'prepare/menu.html', args)