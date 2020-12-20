import login.models
import datetime
import tools.confman
import tools.global_alerts
from science.tools import new_entry

def containsBadChar(stringToCheck:str, exceptions:str = ''):
    badChar = set("¨%\"5+1¶`<0½~¤9]&/*?6:.£7'2¡=8>|}#-´4[(±\@_{§)^€;!,¥$3").difference(set(exceptions))
    return True if set(stringToCheck).intersection(badChar) else False


def getUidFromEmail(newMail):
    user = login.models.User.objects.filter(Email=newMail).values('UserId')
    if user:
        return user[0]["UserId"]
    return False

def registerUser(postData): # Place function somewere else.
    user = login.models.User(Email=postData["email"].lower())
    user.save()
    key = login.models.gen_rsa(login.models.secret_scrambler(postData["password"], user.UserId))

    user.setPubKey(key.publickey().export_key())
    if postData['gender'] == 'Other':
        user.setGender(postData['gender_other'])
    else:
        user.setGender(postData['gender'])
    user.setFirstName(postData['first_name'])
    user.setLastName(postData['last_name'])
    user.setDateOfBirth(postData['date_of_birth'])
    user.setRole('Professional') if 'professional' in postData else user.setRole('User')
    user.setAnonId(key.export_key().decode("utf-8"))
    user.setSymkey()
    user.setCreationDate(datetime.date.today().strftime('%Y-%m-%d'))
    user.save()
    new_entry("PF", user.getAnonId(key.export_key()), f"{postData['date_of_birth']}|{postData['gender'] if postData['gender'] != 'Other' else postData['gender_other']}")
    return user.getUid(), key.export_key(), user.getRole()

def survey_time(request, user, privKey):
    """Check if it is time for survey based on how long ago a user created an account.

    request = request that is sent in to view
    user = current user as User Object
    privKey = users privatekey.
    """
    survey_conf = tools.confman.get_conf(sections=['survey'])['survey']
    universal_lang = tools.confman.get_lang(sections=['universal'])['universal']
    survey_days = survey_conf['links']  # Keys are days and value is link to servey.
    today = datetime.date.today()

    day_diff = today - datetime.date.fromisoformat(user.getCreationDate(privKey))
    if str(day_diff.days) in survey_days.keys():
        link = survey_days[str(day_diff.days)]
        message = universal_lang['long_texts']['survey']
        color = 'warning'
        title = universal_lang['info']

        tools.global_alerts.add_alert(request, color, title, message, link)
