import login.models
import prepare.models
import savemeplan.models
from science.tools import new_entry
from tools.mediaman import delete_file

def addContact(uId, name, phonenumber, available, privKey):
    user = login.models.User.objects.filter(UserId = uId)[0]
    contact = savemeplan.models.Contacts(UserId = user)
    contact.setName(name)
    contact.setPhonenumber(phonenumber)
    contact.setAvailable(available)
    contact.save()
    
def showContacts(uId, PrivKey):
    user = login.models.User.objects.filter(UserId=uId)[0]
    contactsToReturn = []
    contacts = savemeplan.models.Contacts.objects.filter(UserId=user)
    for contact in contacts:
        contactInfo = dict({
            'Id':contact.ContactsId,
            'Name':contact.getName(PrivKey),
            'Phonenumber':contact.getPhonenumber(PrivKey),
            'Available':contact.getAvailable(PrivKey)
        })
        contactsToReturn.append(contactInfo)
    return contactsToReturn

def removeContact(uId, contactId):
    user = login.models.User.objects.filter(UserId=uId)[0]
    savemeplan.models.Contacts.objects.filter(ContactsId=contactId, UserId=user).delete()


def showAllmemories(uId, PrivKey, memType):
    if memType in 'sd':
        memoryIdList=[]
        user=login.models.User.objects.filter(UserId=uId)[0]
        memories = prepare.models.Media.objects.filter(UserId=user)
        for memory in memories:
            if memory.getMemory(PrivKey) == memType:
                memoryInfo = dict({'Title':memory.getMediaTitle(PrivKey),'Id':memory.getMediaId(),'Size':memory.getMediaSize(PrivKey)})
                memoryIdList.append(memoryInfo)
        return memoryIdList
    else:
        return -1

def reencryptMedia(uId, oldPrivKey, newPubKey, newFileNames):
    user=login.models.User.objects.filter(UserId=uId)[0]
    media = prepare.models.Media.objects.filter(UserId=user)
    for mediaObject in media:
        try:
            mediaType = mediaObject.getMediaType(oldPrivKey)
        except ValueError:
            pass
        else:
            mediaObject.setMediaType(newPubKey, mediaType)

        try:
            mediaTitle = mediaObject.getMediaTitle(oldPrivKey)
        except ValueError:
            pass
        else:
            mediaObject.setMediaTitle(newPubKey, mediaTitle)

        try:
            mediaText = mediaObject.getMediaText(oldPrivKey)
        except ValueError:
            pass
        else:
            mediaObject.setMediaText(newPubKey, mediaText)

        try:
            mediaLink = mediaObject.getLink(oldPrivKey)
        except ValueError:
            pass
        else:
            if mediaLink in newFileNames:
                print(f"Medialink old: {mediaLink}")

                mediaLink = newFileNames[mediaLink]
                print(f"MediaLink new: {mediaLink}")
            mediaObject.setLink(newPubKey, mediaLink)

        try:
            memory = mediaObject.getMemory(oldPrivKey)
        except ValueError:
            pass
        else:
            mediaObject.setMemory(newPubKey, memory)

        try:
            mediaSize = mediaObject.getMediaSize(oldPrivKey)
        except ValueError:
            pass
        else:
            mediaObject.setMediaSize(newPubKey, mediaSize)

        mediaObject.save()


def showDiary(uId, symKey):
    user=login.models.User.objects.filter(UserId=uId)[0]
    diary = []
    entries = prepare.models.Diary.objects.filter(UserId=user)
    entries = sortDiary(entries, symKey)
    for entry in entries:
        entry = {
            'EntryDate' : entry.getDate(symKey),
            'Text' : entry.getText(symKey),
            'TimestampCreated' : entry.getTimestamp(symKey),
            'Id' : entry.getDiaryId()
        }
        diary.append(entry)
    return diary

def sortDiary(diary, symKey):
    if len(diary) > 1:
        low = sortDiary(diary[0:len(diary)//2], symKey)
        high = sortDiary(diary[(len(diary)//2):len(diary)], symKey)
        diary = []
        for value in low:
            while high and high[0].lessThan(value, symKey):
                diary.append(high.pop(0))
            diary.append(value)
        if high:
            diary += high
    return diary


def reencryptDiary(user, oldSymKey, newSymkey):
    entries = prepare.models.Diary.objects.filter(UserId=user)
    for entry in entries:
            entry.setDate(newSymkey, entry.getDate(oldSymKey))
            entry.setText(newSymkey, entry.getText(oldSymKey))
            entry.setTimestamp(newSymkey, entry.getTimestamp(oldSymKey))
            entry.save()

def delete_temp_files(session):
    """Delete all temporary decrypted pictures and videos. Will delete
    everything in session key 'files_to_delete' where a filepath is.

    session = The current session. (request.session).
    """
    if "files_to_delete" in session.keys():  # If there is any temporary files not used anymore, delete them
        for file in session["files_to_delete"]:
            splitted_path = file.split("/")
            delete_file("".join(splitted_path[2:]), splitted_path[1])
