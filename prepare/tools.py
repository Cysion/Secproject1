import login.models
import prepare.models
import savemeplan.models
from science.tools import new_entry
from tools.mediaman import delete_file

def addContact(user_id, name, phonenumber, available, privkey):
    """Adds a new contact entry to the database.
    """

    user = login.models.User.objects.filter(UserId = user_id)[0]
    contact = savemeplan.models.Contacts(UserId = user)
    contact.setName(name)
    contact.setPhonenumber(phonenumber)
    contact.setAvailable(available)
    contact.save()
    

def show_contacts(user_id, privkey):
    """Returns a list of dictionaries containing:
        Id = Contact id in database
        Name = Name of the contact
        Phonenumber = Phonenumber of the contact
        Available = When the contact is available
    """

    user = login.models.User.objects.filter(UserId=user_id)[0]
    contacts_to_return = []
    contacts = savemeplan.models.Contacts.objects.filter(UserId=user)
    for contact in contacts:
        contact_info = {
            'Id':contact.ContactsId,
            'Name':contact.getName(privkey),
            'Phonenumber':contact.getPhonenumber(privkey),
            'Available':contact.getAvailable(privkey)
        }
        contacts_to_return.append(contact_info)
    return contacts_to_return


def remove_contact(user_id, contact_id):
    """Removes the contact with contact_id from the database.
    """

    user = login.models.User.objects.filter(UserId=user_id)[0]
    savemeplan.models.Contacts.objects.filter(ContactsId=contact_id, UserId=user).delete()


def show_all_memories(user_id, privkey, mem_type):
    """Returns a list of dictionaries containing:
        Title = Title of the memory entry
        Id = Memory id in database
        Size = Size of the media
    """

    if mem_type in 'sd':
        memory_id_list=[]
        user=login.models.User.objects.filter(UserId=user_id)[0]
        memories = prepare.models.Media.objects.filter(UserId=user)
        for memory in memories:
            if memory.getMemory(privkey) == mem_type:
                memoryInfo = {
                    'Title':memory.getMediaTitle(privkey),
                    'Id':memory.getMediaId(),
                    'Size':memory.getMediaSize(privkey)
                }
                memory_id_list.append(memoryInfo)
        return memory_id_list
    else:
        return -1

def reencrypt_media(user_id, old_privkey, new_pubkey, new_file_names):
    """Reencrypts all of a users memories in the database. This should be done when the password is changed.
    """

    user=login.models.User.objects.filter(UserId=user_id)[0]
    media = prepare.models.Media.objects.filter(UserId=user)
    for media_object in media:
        try:
            mediaType = media_object.getMediaType(old_privkey)
        except ValueError:
            pass
        else:
            media_object.setMediaType(new_pubkey, mediaType)

        try:
            mediaTitle = media_object.getMediaTitle(old_privkey)
        except ValueError:
            pass
        else:
            media_object.setMediaTitle(new_pubkey, mediaTitle)

        try:
            mediaText = media_object.getMediaText(old_privkey)
        except ValueError:
            pass
        else:
            media_object.setMediaText(new_pubkey, mediaText)

        try:
            mediaLink = media_object.getLink(old_privkey)
        except ValueError:
            pass
        else:
            if mediaLink in new_file_names:
                print(f"Medialink old: {mediaLink}")

                mediaLink = new_file_names[mediaLink]
                print(f"MediaLink new: {mediaLink}")
            media_object.setLink(new_pubkey, mediaLink)

        try:
            memory = media_object.getMemory(old_privkey)
        except ValueError:
            pass
        else:
            media_object.setMemory(new_pubkey, memory)

        try:
            mediaSize = media_object.getMediaSize(old_privkey)
        except ValueError:
            pass
        else:
            media_object.setMediaSize(new_pubkey, mediaSize)

        media_object.save()


def show_diary(user_id, symkey, entry_type, user_id_session):
    """Returns a list containing dictionaries containing:
        EntryDate = Date of the diary entry, used for sorting
        Text = Content of the diary entry
        TimestampCreated = Timestamp for when the entry was created, used for sorting
        Id = Diary id in database
        Author = Name of the user who wrote the entry
        AuthorId = User id of the user who wrote the entry
        Owner = True if the current user is the author, otherwise false
        """

    user=login.models.User.objects.filter(UserId=user_id)[0]
    diary = []
    entries = prepare.models.Diary.objects.filter(UserId=user)
    entries = sort_diary(entries, symkey)
    for entry in entries:
        print(entry.EntryType)
        if entry.getEntryType(symkey) == entry_type:
            entry = {
                'EntryDate' : entry.getDate(symkey),
                'Text' : entry.getText(symkey),
                'TimestampCreated' : entry.getTimestamp(symkey),
                'Id' : entry.getDiaryId(),
                'Author' : entry.getAuthor(symkey),
                'AuthorId' : entry.getAuthorId(symkey),
                'Owner' : entry.getAuthorId(symkey) == user_id_session
            }
            diary.append(entry)
    return diary


def sort_diary(diary, symKey):
    """Merge sort to sort diary entries first by EntryDate second by TimestampCreated.
    
    Returns a sorted diary.
    """

    if len(diary) > 1:
        low = sort_diary(diary[0:len(diary)//2], symKey)
        high = sort_diary(diary[(len(diary)//2):len(diary)], symKey)
        diary = []
        for value in low:
            while high and high[0].lessThan(value, symKey):
                diary.append(high.pop(0))
            diary.append(value)
        if high:
            diary += high
    return diary


def reencrypt_diary(user, old_symkey, new_symkey):
    """Reencrypts all of a users diary entries in the database. This should be done when the password is changed.
    """

    entries = prepare.models.Diary.objects.filter(UserId=user)
    for entry in entries:
            entry.setAuthorId(new_symkey, entry.getAuthorId(old_symkey))
            entry.setAuthor(new_symkey, entry.getAuthor(old_symkey))
            entry.setDate(new_symkey, entry.getDate(old_symkey))
            entry.setEntryType(new_symkey, entry.getEntryType(old_symkey))
            entry.setText(new_symkey, entry.getText(old_symkey))
            entry.setTimestamp(new_symkey, entry.getTimestamp(old_symkey))
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
