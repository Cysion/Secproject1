from django.shortcuts import render
from datetime import date
# Create your views here.


from tools.confman import get_lang

UNIVERSAL_LANG = get_lang(sections=["universal"])

def RegisterView(request):

    formtext = get_lang(sections=["login"])

    if request.method == 'POST':
        registerUser()
    else:
        today_date = str(date.today())
        args = {
            'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
            'date': today_date,
            'form': formtext["login"]["form"]
        }
        return render(request, 'login/register.html', args)


def registerUser():
    return None
