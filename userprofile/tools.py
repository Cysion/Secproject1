import login.models
import tools.crypto
import userprofile.models
from django.db import transaction
import tools.mediaman
import prepare.tools
import savemeplan.tools



def changePass(uId:int, PrivKey, newPassword:str):
    user=login.models.User.objects.filter(UserId=uId)[0]
    firstName=user.getFirstName(PrivKey)
    lastName=user.getLastName(PrivKey)
    gender=user.getGender(PrivKey)
    dateOfBirth=user.getDateOfBirth(PrivKey)
    oldSymKey=user.getSymKey(PrivKey)
    anonId = user.getAnonId(PrivKey)

    key = tools.crypto.gen_rsa(tools.crypto.secret_scrambler(newPassword, uId))
    pubkey=key.publickey().export_key()
    PrivKeyNew = key.export_key().decode("utf-8")
    with transaction.atomic():
        user.setPubKey(pubkey)
        user.setGender(gender)
        user.setFirstName(firstName.capitalize())
        user.setLastName(lastName.capitalize())
        user.setDateOfBirth(dateOfBirth)
        retVal = tools.mediaman.reencrypt_user(anonId, oldSymKey)
        newSymkey = retVal[0]
        user.setSymkey(newSymkey)
        user.setAnonId(PrivKeyNew)
        user.save()

        prepare.tools.reencryptDiary(user, oldSymKey, newSymkey)
        prepare.tools.reencryptMedia(user.getUid(), PrivKey, pubkey, retVal[1])
        savemeplan.tools.reencrypt_savemeplan(user, oldSymKey, newSymkey)

        relationsTo = userprofile.models.RelationTo.objects.filter(UserIdFrom=user.getUid())
        for relation in relationsTo:
            reciever = login.models.User.objects.filter(UserId=relation.getUserIdToDecryptedFrom(PrivKey))[0]
            relation.setFromPrivEncrypted(reciever.getPubkey(), key.export_key().decode("utf-8"))
            relation.setUserIdToEncryptedFrom(pubkey, reciever.getUid())
            relation.save()

        return key.export_key()

    return 0

def checkPassword(uId:int, PrivKey, password:str):
    return tools.crypto.gen_rsa(tools.crypto.secret_scrambler(password, uId)).export_key().decode("utf-8") == PrivKey




def createRelation(uId:int, PrivKey, recieverEmail:str, permissions:str):
    """Returns 1 if relation is added or 0 if it failed.
    permissions is a binary string containing 5 bits representing
    Profile
    SaveMePlan
    Check
    Prepare
    Media
    """
    user = login.models.User.objects.filter(UserId=uId)[0]
    reciever = login.models.User.objects.filter(Email=recieverEmail.lower())[0]

    #try:
    with transaction.atomic():
        relationFromEntry = userprofile.models.RelationFrom(
            AnonymityIdFrom = user.getAnonId(PrivKey),
            UserIdTo = reciever,
            Permission = permissions,
            UserIdFromEncrypted = tools.crypto.rsa_encrypt( reciever.getPubkey(), str(user.getUid()).encode("utf-8"))
        )
        relationFromEntry.save()
        print(reciever)
        relationToEntry = userprofile.models.RelationTo(
            UserIdFrom = user,
            Permission = permissions,
            UserIdToEncryptedTo = tools.crypto.rsa_encrypt(reciever.getPubkey(),str(reciever.getUid()).encode("utf-8")),
            UserIdToEncryptedFrom = tools.crypto.rsa_encrypt(user.getPubkey(),str(reciever.getUid()).encode("utf-8")),
            FromPrivEncrypted = tools.crypto.rsa_encrypt_long(reciever.getPubkey(), PrivKey.encode("utf-8"))
        )
        relationToEntry.save()
    #except: #Exeption as e: #Possible exceptions here
        #return 1
    #else:
    return 0

def updateRelationTo(recieverUId:int, recieverPrivKey):
    """Because a user sharing data cannot complete the RelationTo entry, it has to be updated by the reciever.
    Returns 1 on success, 0 on failure"""
    reciever = login.models.User.objects.filter(UserId=recieverUId)[0]
    relationsFrom = userprofile.models.RelationFrom.objects.filter(UserIdTo=reciever)
    relationsToReciever = userprofile.models.RelationTo.objects.filter(AnonymityIdTo=reciever.getAnonId(recieverPrivKey))
    if(len(relationsFrom) != len(relationsToReciever)):
        diff = abs(len(relationsFrom) - len(relationsToReciever))
        print(diff)
        for relationFrom in relationsFrom:
            relationFrom.getUserIdFromDecrypted(recieverPrivKey)
            relationsTo = userprofile.models.RelationTo.objects.filter(UserIdFrom=login.models.User.objects.filter(UserId=relationFrom.getUserIdFromDecrypted(recieverPrivKey))[0])
            for relationTo in relationsTo:
                print(relationTo)
                try:
                    uIdTo = relationTo.getUserIdToDecryptedTo(recieverPrivKey)
                except ValueError:
                    pass
                else:
                    if uIdTo == reciever.getUid():
                        if relationTo.getAnonymityIdTo() != reciever.getAnonId(recieverPrivKey):
                            relationTo.setAnonymityIdTo(reciever.getAnonId(recieverPrivKey))
                            relationTo.save()
                            diff -= 1
                            if not diff:

                                return 1
        return 0
    else:
        return 1


def showAllRelationsTo(uId, PrivKey):
    """Returns the email address of everyone who the user shares data with"""
    user = login.models.User.objects.filter(UserId=uId)[0]
    relationsFrom = userprofile.models.RelationFrom.objects.filter(AnonymityIdFrom=user.getAnonId(PrivKey))
    return [{'Email':relation.getUserIdTo().getEmail(), 'RelationFrom': relation.getRelationFromId()} for relation in relationsFrom]


def showAllRelationsFrom(recieverUId, recieverPrivKey):
    reciever = login.models.User.objects.filter(UserId=recieverUId)[0]
    relationsTo = userprofile.models.RelationTo.objects.filter(AnonymityIdTo=reciever.getAnonId(recieverPrivKey))
    toReturn = []
    for relation in relationsTo:
        userDict = dict()
        userDict['FirstName'] = relation.getUserIdFrom().getFirstName(relation.getFromPrivDecrypted(recieverPrivKey).decode("utf-8"))
        userDict['LastName'] = relation.getUserIdFrom().getLastName(relation.getFromPrivDecrypted(recieverPrivKey).decode("utf-8"))
        userDict['UserId'] = relation.getUserIdFrom().getUid()
        permissions = dict()
        permissions['Profile'] = int(relation.getPermission()[0])
        permissions['SaveMePlan'] = int(relation.getPermission()[1])
        permissions['Check'] = int(relation.getPermission()[2])
        permissions['Prepare'] = int(relation.getPermission()[3])
        permissions['Media'] = int(relation.getPermission()[4])
        userDict['Permissions'] = permissions
        toReturn.append(userDict)
    return toReturn

def removeRelation(uId, PrivKey, recieverEmail):
    user = login.models.User.objects.filter(UserId=uId)[0]
    reciever = login.models.User.objects.filter(Email=recieverEmail.lower())[0]

    with transaction.atomic():
        userprofile.models.RelationFrom.objects.filter(AnonymityIdFrom=user.getAnonId(PrivKey), UserIdTo=reciever.getUid()).delete()
        relationsTo = userprofile.models.RelationTo.objects.filter(UserIdFrom=user)
        for relationTo in relationsTo:
            if relationTo.getUserIdToDecryptedFrom(PrivKey) == reciever.getUid():
                relationToId = relationTo.getRelationToId()
                relationsTo.filter(RelationToId=relationToId).delete()
        return 0
    return 1

def modifyRelation(uId, PrivKey, recieverEmail, permission):
    permissionString = '1'
    permissionString += str(permission['SaveMePlan'])
    permissionString += str(permission['Check'])
    permissionString += str(permission['Prepare'])
    permissionString += str(permission['Media'])

    user = login.models.User.objects.filter(UserId=uId)[0]
    reciever = login.models.User.objects.filter(Email=recieverEmail.lower())[0]
    with transaction.atomic():
        relationFrom=userprofile.models.RelationFrom.objects.filter(AnonymityIdFrom=user.getAnonId(PrivKey), UserIdTo=reciever.getUid())[0]
        relationFrom.setPermission(permissionString)
        relationFrom.save()
        relationsTo = userprofile.models.RelationTo.objects.filter(UserIdFrom=user)
        for relationTo in relationsTo:
            if relationTo.getUserIdToDecryptedFrom(PrivKey) == reciever.getUid():
                relationTo.setPermission(permissionString)
                relationTo.save()
        return 0
    return 1

def removeAllOfUsersRelations(uId, PrivKey):
    user = login.models.User.objects.filter(UserId=uId)[0]
    userprofile.models.RelationFrom.objects.filter(AnonymityIdFrom=user.getAnonId(PrivKey)).delete()
    userprofile.models.RelationTo.objects.filter(UserIdFrom=user).delete()



def getPermissions(userId, recieverId, recieverPrivKey):
    reciever = login.models.User.objects.filter(UserId=recieverId)[0]
    relationTo = userprofile.models.RelationTo.objects.filter(UserIdFrom=userId, AnonymityIdTo=reciever.getAnonId(recieverPrivKey))
    if relationTo:
        relationTo = relationTo[0]
        return relationTo.getPermission()
    else:
        return '00000'

def sharesDataWith(userId, recieverId, recieverPrivKey, data):
    reciever = login.models.User.objects.filter(UserId=recieverId)[0]
    relationTo = userprofile.models.RelationTo.objects.filter(UserIdFrom=userId, AnonymityIdTo=reciever.getAnonId(recieverPrivKey))
    if relationTo:
        relationTo = relationTo[0]
        permission = relationTo.getPermission()
        if data == 'profile':
            if permission[0] == '1':
                return relationTo.getFromPrivDecrypted(recieverPrivKey)
            else:
                return False
        elif data == 'saveMePlan':
            if permission[1] == '1':
                return relationTo.getFromPrivDecrypted(recieverPrivKey)
            else:
                return False
        elif data == 'check':
            if permission[2] == '1':
                return relationTo.getFromPrivDecrypted(recieverPrivKey)
            else:
                return False
        elif data == 'prepare':
            if permission[3] == '1':
                return relationTo.getFromPrivDecrypted(recieverPrivKey)
            else:
                return False
        elif data == 'media':
            if permission[4] == '1':
                return relationTo.getFromPrivDecrypted(recieverPrivKey)
            else:
                return False
        else:
            return False
    else:
        return False