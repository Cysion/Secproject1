import login.models
import tools.crypto
import userprofile.models
from django.db import transaction
import tools.mediaman
import prepare.tools
import savemeplan.tools
import check.tools



def change_pass(user_id:int, privkey, new_password:str, role:str):
    """Changes a users password and reencrypts all data.

    user_id = User id of user changing password
    privkey = Old private key of user changing password
    new_password = New password
    role = Either 'User' or 'Professional'

    Returns the new private key if successful or 0 if failed.
    """

    user=login.models.User.objects.filter(UserId=user_id)[0]
    first_name=user.getFirstName(privkey)
    last_name=user.getLastName(privkey)
    gender=user.getGender(privkey)
    date_of_birth=user.getDateOfBirth(privkey)
    old_symKey=user.getSymKey(privkey)
    anon_id = user.getAnonId(privkey)
    creation_date = user.getCreationDate(privkey)

    key = tools.crypto.gen_rsa(tools.crypto.secret_scrambler(new_password, user_id))
    pubkey=key.publickey().export_key()
    privkey_new = key.export_key().decode("utf-8")
    with transaction.atomic():
        user.setPubKey(pubkey)
        user.setGender(gender)
        user.setFirstName(first_name.capitalize())
        user.setLastName(last_name.capitalize())
        user.setDateOfBirth(date_of_birth)
        ret_val = tools.mediaman.reencrypt_user(anon_id, old_symKey)
        new_symkey = ret_val[0]
        user.setSymkey(new_symkey)
        user.setAnonId(privkey_new)
        user.setCreationDate(creation_date)
        user.save()

        prepare.tools.reencryptDiary(user, old_symKey, new_symkey)
        prepare.tools.reencryptMedia(user.getUid(), privkey, pubkey, ret_val[1])
        savemeplan.tools.reencrypt_savemeplan(user, old_symKey, new_symkey)
        check.tools.reencrypt_check(user, old_symKey, new_symkey)

        if role == 'User':
            relations_to = userprofile.models.RelationTo.objects.filter(UserIdFrom=user.getUid())
            for relation in relations_to:
                reciever = login.models.User.objects.filter(UserId=relation.getUserIdToDecryptedFrom(privkey))[0]
                relation.setFromPrivEncrypted(reciever.getPubkey(), key.export_key().decode("utf-8"))
                relation.setUserIdToEncryptedFrom(pubkey, reciever.getUid())
                relation.save()
        elif role == 'Professional':
            relations_to = userprofile.models.RelationTo.objects.filter(AnonymityIdTo=user.getAnonId(privkey_new))
            for relation in relations_to:
                relation.setUserIdToEncryptedTo(pubkey, relation.getUserIdToDecryptedTo(privkey))
                relation.setFromPrivEncrypted(pubkey, relation.getFromPrivDecrypted(privkey).decode("utf-8"))
                relation.save()
            relations_from = userprofile.models.RelationFrom.objects.filter(UserIdTo=user.getUid())
            for relation in relations_from:
                relation.setUserIdFromEncrypted(pubkey, relation.getUserIdFromDecrypted(privkey))
                relation.save()

        return key.export_key()

    return 0


def check_password(user_id:int, privkey, password:str):
    """Checks a password against the private key of a logged in user
    user_id = User id
    privkey = Old private key
    password = Entered password

    Returns True if password is correct, False if password is wrong
    """

    return tools.crypto.gen_rsa(tools.crypto.secret_scrambler(password, user_id)).export_key().decode("utf-8") == privkey


def create_relation(user_id:int, privkey, reciever_email:str, permissions:str):
    """Creates new entries in RelationFrom and RelationTo. update_relation_to needs to be run
    from the recievers end for the tables to be complete.

    user_id = User id
    privkey = Old private key
    reciever_email = Recievers email address
    permissions = Binary string containing 5 bits representing:
        Profile
        SaveMePlan
        Check
        Prepare
        Media

    Returns 1 if relation is added or 0 if it failed.
    """

    user = login.models.User.objects.filter(UserId=user_id)[0]
    reciever = login.models.User.objects.filter(Email=reciever_email.lower())[0]

    with transaction.atomic():
        relationFromEntry = userprofile.models.RelationFrom(
            AnonymityIdFrom = user.getAnonId(privkey),
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
            FromPrivEncrypted = tools.crypto.rsa_encrypt_long(reciever.getPubkey(), privkey.encode("utf-8"))
        )
        relationToEntry.save()
    return 0

def update_relation_to(reciever_user_id:int, reciever_privkey):
    """Because a user sharing data cannot complete the RelationTo entry, it has to be updated by the reciever.

    reciever_user_id = user id of reciever
    reciever_privkey = private key of reciever

    Returns 1 on success, 0 on failure"""

    reciever = login.models.User.objects.filter(UserId=reciever_user_id)[0]
    relations_from = userprofile.models.RelationFrom.objects.filter(UserIdTo=reciever)
    relations_to_reciever = userprofile.models.RelationTo.objects.filter(AnonymityIdTo=reciever.getAnonId(reciever_privkey))
    if(len(relations_from) != len(relations_to_reciever)):
        diff = abs(len(relations_from) - len(relations_to_reciever))
        print(diff)
        for relation_from in relations_from:
            relation_from.getUserIdFromDecrypted(reciever_privkey)
            relations_to = userprofile.models.RelationTo.objects.filter(UserIdFrom=login.models.User.objects.filter(UserId=relation_from.getUserIdFromDecrypted(reciever_privkey))[0])
            for relation_to in relations_to:
                print(relation_to)
                try:
                    user_id_to = relation_to.getUserIdToDecryptedTo(reciever_privkey)
                except ValueError:
                    pass
                else:
                    if user_id_to == reciever.getUid():
                        if relation_to.getAnonymityIdTo() != reciever.getAnonId(reciever_privkey):
                            relation_to.setAnonymityIdTo(reciever.getAnonId(reciever_privkey))
                            relation_to.save()
                            diff -= 1
                            if not diff:

                                return 1
        return 0
    else:
        return 1


def show_all_relations_to(user_id, privkey):
    """Returns the email address of everyone who the user shares data with and the corresponding RelationFrom id"""

    user = login.models.User.objects.filter(UserId=user_id)[0]
    relations_from = userprofile.models.RelationFrom.objects.filter(AnonymityIdFrom=user.getAnonId(privkey))
    return [{'Email':relation.getUserIdTo().getEmail(), 'RelationFrom': relation.getRelationFromId()} for relation in relations_from]


def show_all_relations_from(reciever_user_id, reciever_privkey):
    """Returns a dictionary for each user who shares data with the reciever. The dictionary contains:
        FirstName
        LastName
        UserId
        Permissions = dictionary containing:
            Profile = 1 or 0 (grant or deny permission)
            SaveMePlan = 1 or 0 (grant or deny permission)
            Check = 1 or 0 (grant or deny permission)
            Prepare = 1 or 0 (grant or deny permission)
            Media = 1 or 0 (grant or deny permission)"""

    reciever = login.models.User.objects.filter(UserId=reciever_user_id)[0]
    relations_to = userprofile.models.RelationTo.objects.filter(AnonymityIdTo=reciever.getAnonId(reciever_privkey))
    toReturn = []
    for relation in relations_to:
        userDict = dict()
        userDict['FirstName'] = relation.getUserIdFrom().getFirstName(relation.getFromPrivDecrypted(reciever_privkey).decode("utf-8"))
        userDict['LastName'] = relation.getUserIdFrom().getLastName(relation.getFromPrivDecrypted(reciever_privkey).decode("utf-8"))
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

def remove_relation(user_id, privkey, reciever_email):
    """Removes a specific relation from user with user_id and reciever with reciever_email"""
    user = login.models.User.objects.filter(UserId=user_id)[0]
    reciever = login.models.User.objects.filter(Email=reciever_email.lower())[0]

    with transaction.atomic():
        userprofile.models.RelationFrom.objects.filter(AnonymityIdFrom=user.getAnonId(privkey), UserIdTo=reciever.getUid()).delete()
        relations_to = userprofile.models.RelationTo.objects.filter(UserIdFrom=user)
        for relation_to in relations_to:
            if relation_to.getUserIdToDecryptedFrom(privkey) == reciever.getUid():
                relation_to_id = relation_to.getRelationToId()
                relations_to.filter(RelationToId=relation_to_id).delete()
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

def removeAllOfProfessionalsRelations(uId, PrivKey):
    user = login.models.User.objects.filter(UserId=uId)[0]
    userprofile.models.RelationFrom.objects.filter(UserIdTo=user).delete()
    userprofile.models.RelationTo.objects.filter(AnonymityIdTo=user.getAnonId(PrivKey)).delete()

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
