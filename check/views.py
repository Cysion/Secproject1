from django.shortcuts import render


# Create your views here.


from tools.confman import get_lang, get_conf
from prepare.tools import delete_temp_files


UNIVERSAL_LANG = get_lang(sections=["universal"])

def GreenCaseView(request):

    delete_temp_files(request.session)

    check_lang = get_lang(sections=["check"])

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'check': check_lang["check"]
    }

    return render(request, 'check/green_case.html', args)


def WellFeelingView(request):

    delete_temp_files(request.session)

    check_lang = get_lang(sections=["check"])

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'check': check_lang["check"]
    }

    return render(request, 'check/well_feeling.html', args)


def SaveMePlanView(request):

    delete_temp_files(request.session)

    check_lang = get_lang(sections=["check"])

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'check': check_lang["check"]
    }

    return render(request, 'check/save_me_plan.html', args)


def PracticeSelfCareView(request):

    delete_temp_files(request.session)

    check_lang = get_lang(sections=["check"])

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'check': check_lang["check"]
    }

    return render(request, 'check/practice_self_care.html', args)
