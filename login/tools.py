import login.models

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
    user.setRole('professional') if 'professional' in postData else user.setRole('User')
    user.setAnonId(key.export_key().decode("utf-8"))
    user.setSymkey()
    user.save()
    #new_entry("PROFILE", user.getAnonId(key.export_key()), f"{postData['date_of_birth']}|{postData['gender'] if postData['gender'] != 'Other' else postData['gender_other']}")
    return user.getUid(), key.export_key(), user.getRole()

