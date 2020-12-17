from django.shortcuts import render
from tools.confman import get_lang, get_conf
from info.tools import open_text
from science.tools import new_entry
import login.models

UNIVERSAL_LANG = get_lang(sections=["universal"])

def MenuView(request):

    info_lang = get_lang(sections=["info"])

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'info': info_lang["info"]
    }
    user = login.models.User.objects.filter(pk=request.session["UserId"])[0]
    new_entry("g1", user.getAnonId(request.session["PrivKey"]), "info")
    return render(request, 'info/menu.html', args)


def AboutView(request):

    info_lang = get_lang(sections=["info"])

    txt = 'about.txt'
        
    text = open_text(txt)

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'info': info_lang["info"],
        'text': text
    }
    user = login.models.User.objects.filter(pk=request.session["UserId"])[0]
    new_entry("i1", user.getAnonId(request.session["PrivKey"]), "abt")
    
    return render(request, 'info/about.html', args)


def HowToView(request):

    info_lang = get_lang(sections=["info"])

    txt = 'howto.txt'
        
    text = open_text(txt)

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'info': info_lang["info"],
        'text': text
    }
    user = login.models.User.objects.filter(pk=request.session["UserId"])[0]
    new_entry("i1", user.getAnonId(request.session["PrivKey"]), "how")
    
    return render(request, 'info/howto.html', args)


def PrivacyGDPRView(request):

    info_lang = get_lang(sections=["info"])

    txt = 'privacy_gdpr.txt'
        
    text = open_text(txt)

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'info': info_lang["info"],
        'text': text
    }
    user = login.models.User.objects.filter(pk=request.session["UserId"])[0]
    new_entry("i1", user.getAnonId(request.session["PrivKey"]), "gdpr")
    
    return render(request, 'info/privacy-gdpr.html', args)


def VolunteeringDisclaimerView(request):

    info_lang = get_lang(sections=["info"])

    txt1 = 'volunteering.txt'
    txt2 = 'disclaimer.txt'
        
    text1 = open_text(txt1)
    text2 = open_text(txt2)

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'info': info_lang["info"],
        'text1': text1,
        'text2': text2
    }
    
    user = login.models.User.objects.filter(pk=request.session["UserId"])[0]
    new_entry("i1", user.getAnonId(request.session["PrivKey"]), "vol")
    return render(request, 'info/volunteering_disclaimer.html', args)


def ToSView(request):

    info_lang = get_lang(sections=["info"])

    txt = 'tos.txt'
        
    text = open_text(txt)

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'info': info_lang["info"],
        'text': text
    }
    user = login.models.User.objects.filter(pk=request.session["UserId"])[0]
    new_entry("i1", user.getAnonId(request.session["PrivKey"]), "tos")
    
    return render(request, 'info/tos.html', args)