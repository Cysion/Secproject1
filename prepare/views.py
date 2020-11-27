from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.

from login.models import User
from prepare.models import Media
from tools.confman import get_lang, get_conf
from tools.mediaman import *
from savemeplan.models import Contacts

UNIVERSAL_LANG = get_lang(sections=["universal"])


def MenuView(request, page=0):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    prepare_lang = get_lang(sections=["prepare"])
    template = 'prepare/menu.html'
    memories = []

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
        template = 'prepare/5_contacts.html'
    elif page == 6:
        template = 'prepare/6_wheretocall.html'
    elif page == 7:
        template = 'prepare/7_diary.html'
    elif page == 8:
        template = 'prepare/8_therapynotes.html'
    else:
        template = 'prepare/menu.html'


    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'prepare': prepare_lang["prepare"],
        'nav': prepare_lang["prepare"]["nav"],
        'memories':memories
    }
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

    memType=request.GET['memType']

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
    if request.POST:  # Cant use method here because of two methods are used.
        if ('title' in request.POST.keys() and len(request.POST["title"]) <= 64
                and len(request.POST["title"]) > 0):

            user = User.objects.filter(pk=request.session["UserId"])[0]
            memory = user.media_set.create()  # Create a Media entry with foreignkey this user.
            memory.setMediaTitle(user.getPubkey(), request.POST["title"])
            memory.setMediaSize(user.getPubkey(), 0)
            memory.setMemory(user.getPubkey(), memType)


            if 'type' in request.POST.keys() and len(request.POST["type"]) > 0:
                memory.setMediaType(user.getPubkey(), request.POST["type"])

                if "link" in request.POST.keys():  # Optional
                    memory.setLink(user.getPubkey(), request.POST["link"])
                elif "media" in request.FILES.keys():  # Optional

                    if (request.FILES["media"].size < int(media_conf["max_size_mb"])*1000000 and
                            "." + request.FILES["media"].name.split(".")[-1].upper() in allowed_extenssions):
                        medias = user.media_set.exclude(pk=memory.MediaId)
                        total_space_used = 0
                        for media in medias:
                            total_space_used += int(media.getMediaSize(request.session["privKey"]))

                        if total_space_used + int(request.FILES["media"].size) <= int(media_conf["max_per_user"])*1000000:
                            try:
                                file = save_file(
                                    user.getSymKey(request.session["privKey"]),
                                    request.FILES["media"].read(),
                                    user.getAnonId(request.session["privKey"])
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

                if 'media_text' in request.POST.keys() and not alerts:  # Optional
                    memory.setMediaText(user.getPubkey(), request.POST["media_text"])

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

                        # return HttpResponseRedirect(reverse('prepare:memory'))


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
        if request.GET["media_type"] and request.GET["media_type"] == "url":  # Display file input type
            media_type = "url"
        elif request.GET["media_type"] and request.GET["media_type"] == "file":   # Display text input type
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
        'lang': prepare_lang["prepare"],
        'error': UNIVERSAL_LANG["universal"]["error"],
        'alerts': alerts,
        'max_file_size': int(media_conf["max_size_mb"]),
    }

    return render(request, 'prepare/add_memory.html', args)

def MemoryView(request, id):

    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    media = Media.objects.filter(MediaId=id)[0]
    user = User.object.filter(UserId=request.session['UserId'])
    if not media.getUserId()==user:
        return 404 #Lägg in Djangofunktion för detta

    prepare_lang = get_lang(sections=["prepare"])

    allowed_extenssions = [  # Some of the more popular allowed formats
    #  Videos 
    dict({'video':[
    ".WEBM", ".MPG", ".MP2", ".MPEG",
    ".MPE", ".MPV", ".OGG", ".MP4", ".M4P", ".M4V", ".AVI",
    ".WMV", ".MOV", ".QT", ".FLV", ".SWF", ".AVCHD"]}),

    # Photos
    dict({'photo':[
    ".JPG", ".JPEG", ".EXIF", ".GIF", ".BMP", ".PNG",
    ".WEBP", ".HEIF"]}),

    # Sound
    dict({'sound':[
    ".AA", ".AAX", ".AIFF", ".ALAC", ".DVF", ".M4A", ".M4B",
    ".MMF", ".MP3", ".MPC", ".OPUS", ".RF64", ".MAV", ".WMA",
    ".WV"]})
    ]

    supported_links = ['instagram', 'youtube', 'youtu', 'tictoc']
    content = dict()

    link = media.getLink(request.session['PrivKey'])

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset


    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
        "add_memory": prepare_lang["prepare"]["long_texts"]["add_memory"],
        "content": content
    }

    return render(request, 'prepare/memory.html', args)


def ContactsView(request):
    
    return render(request, 'prepare/contacts.html')



def addContact(uId, name, phonenumber, available):
    contact = Contacts(
        Name = name,
        Phonenumber = phonenumber,
        Available = available
    )
    contact.save()

def showContacts(uId, privKey):
    user = User.objects.filter(UserId=uId)[0]
    contactsToReturn = []
    contacts = Contacts.objects.filter(UserId=user)
    for contact in contacts:
        contactInfo = dict({
            'Name':contact.getName(privKey),
            'Phonenumber':contact.getPhonenumber(privKey),
            'Available':contact.getAvailable(privKey)
        })
        contactsToReturn.append(contactInfo)
    return contactsToReturn

def showAllmemories(uId, privKey, memType):
    if memType in 'sd':
        memoryIdList=[]
        user=User.objects.filter(UserId=uId)[0]
        memories = Media.objects.filter(UserId=user, Memory=memType)
        for memory in memories:
            memoryInfo = dict({'Title':memory.getMediaTitle(privKey),'Id':memory.getMediaId()})
            memoryIdList.append(memoryInfo)
        return memoryIdList
    else:
        return -1
