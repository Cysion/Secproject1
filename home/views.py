from django.shortcuts import render
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.

from login.models import User
import datetime
from tools.confman import get_lang

UNIVERSAL_LANG = get_lang(sections=["universal"])

def IndexView(request):

    home_lang = get_lang(sections=["home"])

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'home': home_lang["home"]
    }
    return render(request, 'home/index.html', args)

def ShowcaseView(request):
    try:
        # Först testar jag att skapa 2 användare och lägga in dem i tabellen
        user1 = User(
            Gender='Male',
            FirstName='Kevin',
            LastName='Engström',
            DateOfBirth=datetime.date.today(),
            Email='kevin@kevin.kevin',
            Pubkey='asd',
        )
        user1.save()

        user2 = User(
            Gender='Female',
            FirstName='Lisa',
            LastName='Svensson',
            DateOfBirth=datetime.date.today(),
            Email='lisa@lisa.lisa',
            Pubkey='fgh',
        )
        user2.save()
    except Exception as e:
        pass

    # En enkel sökning där jag vill ta fram alla som heter lisa. Och jag vill bara ha attributen id, förnamn och födelsedag
    result = User.objects.filter(FirstName='Lisa').values(
        'UserId', 'FirstName', 'DateOfBirth'
    )

    # För att skicka in variabler till templaten så ska en dict skickas med variablerna.
    context = {'result': result[0]}

    return render(request, 'home/showcase.html', {})
