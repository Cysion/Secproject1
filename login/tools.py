import login.models
import datetime
import tools.confman
import tools.global_alerts
from science.tools import new_entry

def contains_bad_char(string_to_check:str, exceptions:str = ''):
    """Checks a string for forbidden characters
    
    string_to_check = String to be checked
    exceptions = string containing characters that should be allowed
    """

    bad_char = set("¨%\"5+1¶`<0½~¤9]&/*?6:.£7'2¡=8>|}#-´4[(±\@_{§)^€;!,¥$3").difference(set(exceptions))
    return True if set(string_to_check).intersection(bad_char) else False

def register_user(post_data):
    """Creates a new User entry in the database

    post_data = dictionary containing the following keys:
        email = email address
        gender = Male, Female or Other
        gender_other = string that is used as gender if gender is Other
        first_name = first name
        last_name = last name
        date_of_birth = date of birth
        professional = Optional, used if the new user is a professional user
    """

    user = login.models.User(Email=post_data["email"].lower())
    user.save()
    key = login.models.gen_rsa(login.models.secret_scrambler(post_data["password"], user.UserId))

    user.setPubKey(key.publickey().export_key())
    if post_data['gender'] == 'Other':
        user.setGender(post_data['gender_other'])
    else:
        user.setGender(post_data['gender'])
    user.setFirstName(post_data['first_name'])
    user.setLastName(post_data['last_name'])
    user.setDateOfBirth(post_data['date_of_birth'])
    user.setRole('Professional') if 'professional' in post_data else user.setRole('User')
    user.setAnonId(key.export_key().decode("utf-8"))
    user.setSymkey()
    user.setCreationDate(datetime.date.today().strftime('%Y-%m-%d'))
    user.save()
    new_entry("PF", user.getAnonId(key.export_key()), f"{post_data['date_of_birth']}|{post_data['gender'] if post_data['gender'] != 'Other' else post_data['gender_other']}")
    return user.getUid(), key.export_key(), user.getRole()

def survey_time(request, user, privkey):
    """Check if it is time for survey based on how long ago a user created an account.

    request = request that is sent in to view
    user = current user as User Object
    privKey = users privatekey.
    """

    survey_conf = tools.confman.get_conf(sections=['survey'])['survey']
    universal_lang = tools.confman.get_lang(sections=['universal'])['universal']
    survey_days = survey_conf['links']  # Keys are days and value is link to servey.
    today = datetime.date.today()

    day_diff = today - datetime.date.fromisoformat(user.getCreationDate(privkey))
    if str(day_diff.days) in survey_days.keys():
        link = survey_days[str(day_diff.days)]
        message = universal_lang['long_texts']['survey']
        color = 'warning'
        title = universal_lang['info']

        tools.global_alerts.add_alert(request, color, title, message, link)
