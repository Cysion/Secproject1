from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import date
# Create your views here.

from login.models import User
from tools.crypto import gen_rsa, secret_scrambler, rsa_encrypt, rsa_decrypt


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
    if not request.session['UserId']:
        alerts = {}

        login_lang = get_lang(sections=["login"])  # Get language text for form.
        # Check if a user have submitted a form.
        if request.method == 'POST':
            for index in ['first_name','last_name','gender','gender_other', 'email']:
                exceptions = ''
                if index == 'email':
                    exceptions = '1234567890@!#$%&*+-/=?^_`{|}~.'
                if containsBadChar(request.POST[index], exceptions):
                    alerts[index] = "badChar"

            if request.POST["password"] != request.POST["repassword"]:
                alerts['repassword'] = "repassword"
            if getUidFromEmail(request.POST["email"]):
                alerts['email'] = 'email_already_exists'

            if not alerts:
                sessionsData = registerUser(request.POST)
                request.session['UserId'] = sessionsData[0]
                request.session['privKey'] = sessionsData[1]
                return HttpResponseRedirect(reverse('home:index')) # ROBIN!!!!! TITTA HÄR! Den här ska användas vid redirekt när man har successfully loggat in.

        today_date = str(date.today())

        args = {
            'POST': request.POST,
            'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
            'form': login_lang["login"]["form"],
            'alerts': login_lang['login']['long_texts']['alerts'],
            'alert': alerts
        }
        return render(request, 'login/register.html', args)
    return HttpResponseRedirect(reverse('home:index'))

def containsBadChar(stringToCheck:str, exceptions:str = ''):
    badChar = set("¨%\"5+1¶`<0½~¤9]&/*?6:.£7'2¡=8>|}#-´4[(±\@_{§)^€;!,¥$3").difference(set(exceptions))
    return True if set(stringToCheck).intersection(badChar) else False


def getUidFromEmail(newMail):
    result = User.objects.filter(Email=newMail).values('UserId')
    if result:
        return result[0]["UserId"]
    return False


def registerUser(postData): # Place function somewere else.
    user1 = User(
            Gender='temp',
            FirstName='temp',
            LastName='temp',
            DateOfBirth='temp',
            Email=postData["email"]
        )
    user1.save()

    key = gen_rsa(secret_scrambler(postData["password"], user1.UserId))
    pubkey=key.publickey().export_key()

    user1.Pubkey = pubkey
    user1.Gender=rsa_encrypt(pubkey, postData["gender"])
    user1.FirstName=rsa_encrypt(pubkey, postData["first_name"].capitalize())
    user1.LastName=rsa_encrypt(pubkey, postData["last_name"].capitalize())
    user1.DateOfBirth=rsa_encrypt(pubkey, postData["date_of_birth"])


    user1.save()

    return user1.UserId ,pubkey

def LoginView(request):
    if not request.session['UserId']:
        loginFail = False
        if request.method == 'POST':
            
            result = User.objects.filter(Email=request.POST['email']).values('UserId', 'Pubkey')

            if result:
                print(result[0]['UserId'])
                key = gen_rsa(secret_scrambler(request.POST["password"], result[0]['UserId']))
                if str(key.publickey().export_key()) == str(result[0]['Pubkey']):
                    print("Jippeie yaay login successful!")
                    request.session['UserId'] = result[0]['UserId']
                    request.session['privKey'] = key.privatekey().export_key()
                    return HttpResponseRedirect(reverse('home:index'))
                else:
                    loginFail = True
            else:
                loginFail = True

        login_lang = get_lang(sections=["login"])
        wrong_login_enterd = False
        args = {
            'post': request.POST,
            'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
            'form': login_lang["login"]["form"],
            'alerts': login_lang['login']['long_texts']['alerts'],
            'wrong_password_enterd': loginFail  # A check if right login was entered
        }

        return render(request, 'login/login.html', args)
    return HttpResponseRedirect(reverse('home:index'))


def ProfileView(request):
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
    }

    return render(request, 'login/profile.html', args)
