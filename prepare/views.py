from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
# Create your views here.

from login.models import User
from prepare.models import Media
from tools.confman import get_lang, get_conf
from tools.mediaman import get_sha1, save_file, open_file, delete_file
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import login.views
from django.db import transaction

from django.core.files import File
from savemeplan.models import Contacts
from tools.scienceman import new_entry
import time
import re

UNIVERSAL_LANG = get_lang(sections=["universal"])


def MenuView(request, page=0):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    prepare_lang = get_lang(sections=["prepare"])
    template = 'prepare/menu.html'
    memories = []
    contacts = []
    user = User.objects.filter(pk=request.session["UserId"])[0]

    if page == 1:
        template = 'prepare/1_howto.html'
    elif page == 2:
        template = 'prepare/2_practicebreathing.html'
    elif page == 3:
        memories = showAllmemories(request.session['UserId'], request.session['PrivKey'], 's')
        template = 'prepare/3_supportivememories.html'
    elif page == 4:
        memories = showAllmemories(request.session['UserId'], request.session['PrivKey'], 'd')
        template = 'prepare/4_destructivememories.html'
    elif page == 5:
        contacts=showContacts(request.session['UserId'], request.session['PrivKey'])
        template = 'prepare/5_contacts.html'
    elif page == 6:
        template = 'prepare/6_wheretocall.html'
    elif page == 7:
        template = 'prepare/7_diary.html'
    elif page == 8:
        template = 'prepare/8_therapynotes.html'
    else:
        #Science segment
        new_entry("g1", user.getAnonId(request.session['PrivKey']), "prep")

        template = 'prepare/menu.html'


    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'prepare': prepare_lang["prepare"],
        'nav': prepare_lang["prepare"]["nav"],
        'memories':memories,
        'contacts':contacts
    }

    #if 0 < page < 9:
    #    new_entry("p3", user.getAnonId(request.session['PrivKey']), f"step {page}")
    return render(request, template, args)


def addMemoryView(request):
    """View for adding memories.

    POST keys:
    title = The title of the memory. Required!
    media_text = Text. Optional!
    link = A url which can be youtube video or other urls. Optional!
    type = Memory type! Can be Music, Game, Video, Image, Phrase, Story, Award
    or Theme. Take the first and last letter as lower case and you get value
    from type (example mc is Music). Required!

    FILES keys:
    media = Can be image, video or song. Optional!
    """
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    prepare_lang = get_lang(sections=["prepare"])
    media_conf = get_conf(sections=["media"])["media"]
    alerts = {}

    mem_type = ""
    if "mem_type" in request.GET.keys():
        mem_type = request.GET['mem_type']
    elif "mem_type" in request.POST.keys():
        mem_type = request.POST['mem_type']
    else:
        mem_type = "s"

    if mem_type != "s" and mem_type != "d":
        mem_type = "s"

    allowed_extenssions = [  # Some of the more popular allowed formats
        #  Videos
        ".WEBM", ".MPG", ".MP2", ".MPEG",
        ".MPE", ".MPV", ".OGG", ".MP4", ".M4P", ".M4V", ".AVI",
        ".WMV", ".MOV", ".QT", ".FLV", ".SWF", ".AVCHD",

        # Photos
        ".JPG", ".JPEG", ".EXIF", ".GIF", ".BMP", ".PNG",
        ".WEBP", ".HEIF",

        # Sound
        ".AA", ".AAX", ".AIFF", ".ALAC", ".DVF", ".M4A", ".M4B",
        ".MMF", ".MP3", ".MPC", ".OPUS", ".RF64", ".MAV", ".WMA",
        ".WV"
    ]

    media_type = ""  # Used for displaying url input or file input on page.
    if request.POST and "save" in request.POST.keys():  # Cant use method here because of two methods are used.
        if ('title' in request.POST.keys() and len(request.POST["title"]) <= 64
                and len(request.POST["title"]) > 0):

            with transaction.atomic():
                user = User.objects.filter(pk=request.session["UserId"])[0]
                memory = user.media_set.create()  # Create a Media entry with foreignkey this user.
                memory.setMediaTitle(user.getPubkey(), request.POST["title"])
                memory.setMediaSize(user.getPubkey(), 0)
                memory.setMemory(user.getPubkey(), mem_type)


                if 'type' in request.POST.keys() and len(request.POST["type"]) > 0:
                    memory.setMediaType(user.getPubkey(), request.POST["type"])

                    if "link" in request.POST.keys():  # Optional
                        memory.setLink(user.getPubkey(), request.POST["link"])
                    elif "media" in request.FILES.keys():  # Optional

                        if (request.FILES["media"].size < int(media_conf["max_size_mb"])*1000000 and
                                "." + request.FILES["media"].name.split(".")[-1].upper() in allowed_extenssions):

                            medias = user.media_set.exclude(pk=memory.MediaId)  # Get all memories exept current one.
                            total_space_used = 0
                            for media in medias:
                                total_space_used += int(media.getMediaSize(request.session["PrivKey"]))

                            if total_space_used + int(request.FILES["media"].size) <= int(media_conf["max_per_user"])*1000000:
                                try:
                                    file = save_file(
                                        user.getSymKey(request.session["PrivKey"]),
                                        request.FILES["media"].read(),
                                        user.getAnonId(request.session["PrivKey"]),
                                        upload_name=request.FILES["media"].name
                                    )

                                    memory.setMediaSize(user.getPubkey(), request.FILES["media"].size)
                                    memory.setLink(user.getPubkey(), file[0])

                                except RuntimeError as e:
                                    alerts["file"] = prepare_lang["prepare"]["long_texts"]["alerts"]["file_to_big"]
                                    memory.delete()

                                except Exception as e:
                                    alerts["file"] = prepare_lang["prepare"]["long_texts"]["alerts"]["file_error"]
                                    memory.delete()

                            else:
                                alerts["file"] = prepare_lang["prepare"]["long_texts"]["alerts"]["not_enough_space"]
                                memory.delete()

                        else:
                            alerts["file"] = prepare_lang["prepare"]["long_texts"]["alerts"]["file_to_big"]
                            memory.delete()

                    if 'media_text' in request.POST.keys() and len(request.POST["media_text"]) <= 500 and not alerts:  # Optional
                        memory.setMediaText(user.getPubkey(), request.POST["media_text"])
                    else:
                        alerts["text"] = prepare_lang["prepare"]["long_texts"]["alerts"]["text_to_long"]

                    if not alerts and not request.GET:
                        memory.save()
                        alert = {
                            "color": "success",
                            "title": UNIVERSAL_LANG["universal"]["success"],
                            "message": prepare_lang["prepare"]["long_texts"]["alerts"]["memory_added"]
                        }

                        if "global_alerts" not in request.session.keys():  # Check if global_elerts is in session allready.
                            request.session["global_alerts"] = [alert]
                        else:
                            request.session["global_alerts"].append(alert)

                        return HttpResponseRedirect(reverse('prepare:memory', args=(memory.MediaId,)))  # Redirect to created memory


                else:  # If no type is entered
                    alerts["type"] = prepare_lang["prepare"]["long_texts"]["alerts"]["no_type"]
                    memory.delete()

        else:  # If Title is either empty or too long
            if len(request.POST["title"]) >= 64:
                alerts["title"] = prepare_lang["prepare"]["long_texts"]["alerts"]["title_to_long"]
            else:
                alerts["title"] = prepare_lang["prepare"]["long_texts"]["alerts"]["no_title"]
            memory.delete()

        if "link" in request.POST.keys():  # Displaying text input type
            media_type = "url"
        elif "media" in request.FILES.keys():  # Displaying file input type
            media_type = "file"

    if request.GET:
        if "media_type" in request.GET.keys() and request.GET["media_type"] == "url":  # Display file input type
            media_type = "url"
        elif "media_type" in request.GET.keys() and request.GET["media_type"] == "file":   # Display text input type
            media_type = "file"

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'back': UNIVERSAL_LANG["universal"]["back"],
        'media_type': media_type,
        'POST': request.POST,
        'prepare': prepare_lang["prepare"],
        'error': UNIVERSAL_LANG["universal"]["error"],
        'alerts': alerts,
        'max_file_size': int(media_conf["max_size_mb"]),
        'mem_type': mem_type
    }
    #new_entry("m1", user.getAnonId(request.session["PrivKey"]), "na")
    return render(request, 'prepare/add_memory.html', args)

def MemoryView(request, id):

    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    user = User.objects.filter(pk=request.session["UserId"])[0]
    prepare_lang = get_lang(sections=["prepare"])

    content = dict()
    try:
        memory = Media.objects.filter(pk=id)[0]
    except Exception as e:
        return Http404("Memory does not exist!")

    if memory.UserId.UserId != request.session["UserId"]:
        # User dont belong here
        return Http404("Memory does not exist!")

    if "files_to_delete" in request.session.keys():  # If there is any temporary files not used anymore, delete them
        for file in request.session["files_to_delete"]:
            splitted_path = file.split("/")
            delete_file("".join(splitted_path[2:]), splitted_path[1])

    content["id"] = id
    content["title"] = memory.getMediaTitle(request.session["PrivKey"])
    content["type"] = memory.getMemory(request.session["PrivKey"])
    content["size"] = int(memory.getMediaSize(request.session["PrivKey"]))/1000000

    url = ""
    memtype = ""
    file = ""
    unidentified_url = ""

    local_url_pattern = re.compile("^[a-zA-Z0-9]{40}\/([a-zA-Z0-9]{40})$")  # Pattern for local files such as video, photo or sound

    if memory.MediaText:
        content["text"] = memory.getMediaText(request.session["PrivKey"])
    if memory.MediaLink:
        unidentified_url = memory.getLink(request.session["PrivKey"])

    if "youtube.com" in unidentified_url:
        memtype = "youtube"
        index = unidentified_url.find("?v=")
        done = False
        content[memtype] = ""

        for i in range(index+3, len(unidentified_url)):  # get video id of youtube video
            if unidentified_url[i] == "&":
                done = True
            if not done:
                content[memtype] += unidentified_url[i]

    elif "youtu.be" in unidentified_url:
        memtype = "youtube"
        content[memtype] = unidentified_url.split("/")[-1]  # get video id of youtube video

    elif local_url_pattern.match(unidentified_url): 
        url = unidentified_url
        memtype = "photo/video/sound"

    else:
        memtype = "url_other"
        content[memtype] = unidentified_url

    if request.GET and "delete" in request.GET.keys():

        if memtype == "photo/video/sound":
            delete_file(url)
        redirect_path = memory.getMemory(request.session["PrivKey"])  # To know which step to redirect to.
        memory.delete()

        alert = {
            "color": "success",
            "title": UNIVERSAL_LANG["universal"]["warning"],
            "message": prepare_lang["prepare"]["long_texts"]["alerts"]["memory_deleted"]
        }

        if "global_alerts" not in request.session.keys():  # Check if global_elerts is in session allready.
            request.session["global_alerts"] = [alert]
        else:
            request.session["global_alerts"].append(alert)
        
        new_entry("m2", user.getAnonId(request.session["PrivKey"]), "na")
        if redirect_path == "s":
            return HttpResponseRedirect(reverse('prepare:menu-page', args=(3,)))
        else:
            return HttpResponseRedirect(reverse('prepare:menu-page', args=(4,)))

    if memtype == "photo/video/sound":
        photo_extenssions = [  # Some of the more popular allowed formats
            # Photos
            ".JPG", ".JPEG", ".EXIF", ".GIF", ".BMP", ".PNG",
            ".WEBP", ".HEIF",

        ]

        video_extenssions = [
            ".WEBM", ".MPG", ".MP2", ".MPEG",
            ".MPE", ".MPV", ".OGG", ".MP4", ".M4P", ".M4V", ".AVI",
            ".WMV", ".MOV", ".QT", ".FLV", ".SWF", ".AVCHD",
        ]

        sound_extenssions = [
            ".AA", ".AAX", ".AIFF", ".ALAC", ".DVF", ".M4A", ".M4B",
            ".MMF", ".MP3", ".MPC", ".OPUS", ".RF64", ".MAV", ".WMA",
            ".WV"
        ]
        file_type = ""

        try:
            file = open_file(user.getSymKey(request.session["PrivKey"]), url)
            
        except RuntimeError as e:
            alert = {
                "color": "error",
                "title": UNIVERSAL_LANG["universal"]["error"],
                "message": prepare_lang["prepare"]["long_texts"]["alerts"]["checksum_error"]
            }

            if "global_alerts" not in request.session.keys():  # Check if global_elerts is in session allready.
                request.session["global_alerts"] = [alert]
            else:
                request.session["global_alerts"].append(alert)
            return HttpResponseRedirect(reverse('prepare:menu'))

        for line in file[0].split("\n"):
            splitline = line.split(":")
            if splitline[0] == "filetype":
                file_type = splitline[1]

        if "." + file_type.upper() in photo_extenssions:
            memtype = "photo"
        elif "." + file_type.upper() in video_extenssions:
            memtype = "video"
        elif "." + file_type.upper() in sound_extenssions:
            memtype = "sound"
        else:
            memtype = "error"
        
        if memtype != "error":

            file_path = "temp/"
            file_name = str(time.time())
            file_name = "".join(file_name.split("."))

            try:
                default_storage.save(file_path + file_name + "." + file_type, ContentFile(file[1]))

                content[memtype] = "media/" + file_path + file_name + "." + file_type  # Full path to media

                if "files_to_delete" in request.session.keys():
                    request.session["files_to_delete"].append(content[memtype])
                else:
                    request.session["files_to_delete"] = [content[memtype]]
            except Exception as e:
                alert = {
                    "color": "error",
                    "title": UNIVERSAL_LANG["universal"]["error"],
                    "message": prepare_lang["prepare"]["long_texts"]["alerts"]["could_not_open_file"]
                }

                if "global_alerts" not in request.session.keys():  # Check if global_elerts is in session allready.
                    request.session["global_alerts"] = [alert]
                else:
                    request.session["global_alerts"].append(alert)
                return HttpResponseRedirect(reverse('prepare:menu'))

    using_space = prepare_lang["prepare"]["long_texts"]["memory_size"].replace("%mb%", str(int(content["size"])))
    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
        "using_space": using_space,
        "content": content,
        "back": UNIVERSAL_LANG["universal"]["back"],
        'prepare': prepare_lang["prepare"]
    }

    new_entry("m3", user.getAnonId(request.session["PrivKey"]), "na")
    return render(request, 'prepare/memory.html', args)


def ContactsView(request):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))
    alerts = {}
    if request.method == 'POST':
        exceptions = ''
        user = User.objects.filter(UserId=request.session["UserId"])[0]
        prepare_lang = get_lang(sections=["prepare"])
        for index in ['name', 'phonenumber', 'available']:
            if index == 'phonenumber':
                exceptions = '+0123456789'
            if index == 'available':
                exceptions = '0123456789+-/'
            if login.views.containsBadChar(request.POST[index], exceptions):
                alerts[index] = "badChar"
        if not alerts:
            addContact(user.getUid(), request.POST['name'], request.POST['phonenumber'], request.POST['available'], request.session['PrivKey'])
            return HttpResponseRedirect(reverse('prepare:menu-page', args=(5,)))
    
    prepare_lang = get_lang(sections=["prepare"])

    args = {
        'POST': request.POST,
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG['universal']['back'],
        'alert': alerts,
        "back": UNIVERSAL_LANG["universal"]["back"],
        'prepare': prepare_lang["prepare"]
    }
    return render(request, 'prepare/add_contact.html', args)

def editContactsView(request):
    prepare_lang = get_lang(sections=["prepare"])
    args = {
        'POST': request.POST,
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG['universal']['back'],
        'prepare': prepare_lang["prepare"],
        "back": UNIVERSAL_LANG["universal"]["back"],
        'modal': prepare_lang["prepare"]["contacts"]["modal"]
    }
    return render(request, 'prepare/addcontact.html')

def editContactView(request, id):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))
    prepare_lang = get_lang(sections=["prepare"])
    alerts=dict()
    
    user = User.objects.filter(UserId=request.session["UserId"])[0]
    contact = Contacts.objects.filter(ContactsId=id)[0]
    
    if request.method=='POST':
        contact.setName(request.POST['Name'])
        contact.setPhonenumber(request.POST['Phonenumber'])
        contact.setAvailable(request.POST['Available'])
        contact.save()

    contactData = dict({
        'Name': contact.getName(request.session['PrivKey']),
        'Phonenumber':contact.getPhonenumber(request.session['PrivKey']),
        'Available':contact.getAvailable(request.session['PrivKey'])
    })


    args = {
        'POST': request.POST,
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG['universal']['back'],
        'alert': alerts,
        'prepare': prepare_lang["prepare"],
        'modal': prepare_lang["prepare"]["contacts"]["modal"],
        'contact':contactData

    }
    print(args['contact'])
    return render(request, 'prepare/edit_contact.html', args)



def addContact(uId, name, phonenumber, available, privKey):
    user = User.objects.filter(UserId = uId)[0]
    contact = Contacts(UserId = user)
    contact.setName(name)
    contact.setPhonenumber(phonenumber)
    contact.setAvailable(available)
    print(contact.getName(privKey))
    print(contact.getPhonenumber(privKey))
    print(contact.getAvailable(privKey))
    contact.save()

def showContacts(uId, PrivKey):
    user = User.objects.filter(UserId=uId)[0]
    contactsToReturn = []
    contacts = Contacts.objects.filter(UserId=user)
    for contact in contacts:
        contactInfo = dict({
            'Id':contact.ContactsId,
            'Name':contact.getName(PrivKey),
            'Phonenumber':contact.getPhonenumber(PrivKey),
            'Available':contact.getAvailable(PrivKey)
        })
        contactsToReturn.append(contactInfo)
    return contactsToReturn

def showAllmemories(uId, PrivKey, memType):
    if memType in 'sd':
        memoryIdList=[]
        user=User.objects.filter(UserId=uId)[0]
        memories = Media.objects.filter(UserId=user)
        for memory in memories:
            if memory.getMemory(PrivKey) == memType:
                memoryInfo = dict({'Title':memory.getMediaTitle(PrivKey),'Id':memory.getMediaId(),'Size':memory.getMediaSize(PrivKey)})
                memoryIdList.append(memoryInfo)
        return memoryIdList
    else:
        return -1

def reencryptMedia(uId, oldPrivKey, newPubKey, newFileNames):
    user=User.objects.filter(UserId=uId)[0]
    media = Media.objects.filter(UserId=user)
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
