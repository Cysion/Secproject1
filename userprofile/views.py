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
