from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import date
# Create your views here.

from login.models import User
from tools.crypto import gen_rsa, secret_scrambler


from tools.confman import get_lang

UNIVERSAL_LANG = get_lang(sections=["universal"])

def RegisterView(request):
    '''
    This view will display the registration page and when submitting a
    registration it will enter here.

    If submitting a registration POST will contain the following.
        first_name - Users first name
        last_name - Users last name
        date_of_birth - When user was born
        gender - Gender of the user. Is one of the following
            Male
            Female
            Other
        gender_other - If user choose gender=Other this will contain a text.
        email - Users email.
        password - Users entered non hashed password
        repassword - reentered password to dubble check that user entered the
            right one.
        agree_terms - Värdet ska vara "accept"
    '''
    wrong_password_enterd = False
    email_exists = False
    badCharacter = set("!@#$%^&*\";,.:_|<>")



    login_lang = get_lang(sections=["login"])  # Get language text for form.
    # Check if a user have submitted a form.
    if request.method == 'POST':
        statusCheck = registerUser(request.POST)
        if True not in statusCheck:
            return HttpResponseRedirect(reverse('home:index')) # ROBIN!!!!! TITTA HÄR! Den här ska användas vid redirekt när man har successfully loggat in.

        wrong_password_enterd = statusCheck[0]
        email_exists = statusCheck[1]
    today_date = str(date.today())


    args = {
        'POST': request.POST,
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'form': login_lang["login"]["form"],
        'alerts': login_lang['login']['long_texts']['alerts'],
        'pattern': login_lang['login']['long_texts']['allowed_chars'],
        'wrong_password_enterd': wrong_password_enterd,  # A check if right password was entered
        'email_already_exists': email_exists,
        'alert': "a"
    }
    return render(request, 'login/register.html', args)

def getUidFromEmail(newMail):
    result = User.objects.filter(Email=newMail).values('UserId')
    if result:
        return result[0]["UserId"]
    return False


def registerUser(postData): # Place function somewere else.
    if postData["password"] != postData["repassword"]:
            return (True, getUidFromEmail(postData["email"]))
    if getUidFromEmail(postData["email"]):
            return (False, True)

    user1 = User(
            Gender=postData["gender"],
            FirstName=postData["first_name"].capitalize(),
            LastName=postData["last_name"].capitalize(),
            DateOfBirth=postData["date_of_birth"],
            Email=postData["email"]
        )
    user1.save()

    user1.Pubkey=gen_rsa(secret_scrambler(postData["password"], user1.UserId)).publickey().export_key()

    user1.save()

    return (False, False)

def LoginView(request):
    login_lang = get_lang(sections=["login"])
    wrong_login_enterd = False
    args = {
        'post': request.POST,
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'form': login_lang["login"]["form"],
        'alerts': login_lang['login']['long_texts']['alerts'],
        'wrong_password_enterd': wrong_login_enterd  # A check if right login was entered
    }

    return render(request, 'login/login.html', args)
