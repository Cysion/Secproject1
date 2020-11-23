from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.

from login.models import User
from prepare.models import Media
from tools.confman import get_lang, get_conf
from tools.mediaman import *

UNIVERSAL_LANG = get_lang(sections=["universal"])


def MenuView(request):
    prepare_lang = get_lang(sections=["prepare"])
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],
        'back': UNIVERSAL_LANG["universal"]["back"],
        'prepare': prepare_lang["prepare"]
    }
    return render(request, 'prepare/menu.html', args)


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

            current_user = User.objects.filter(pk=request.session["UserId"])[0]
            memory = current_user.media_set.create()  # Create a Media entry with foreignkey this user.
            memory.setMediaTitle(current_user.getPubkey(), request.POST["title"])

            if 'type' in request.POST.keys() and len(request.POST["type"]) > 0:
                memory.setMediaType(current_user.getPubkey(), request.POST["type"])

                if "link" in request.POST.keys():  # Optional
                    memory.setMediaLink(current_user.getPubkey(), request.POST["link"])
                elif "media" in request.FILES.keys():  # Optional

                    if (request.FILES["media"].size < int(media_conf["max_size_mb"])*1000000 and
                            "." + request.FILES["media"].name.split(".")[-1].upper() in allowed_extenssions):
                        try:
                            file = save_file(
                                current_user.getSymKey(request.session["privKey"]),
                                request.FILES["media"].read(),
                                current_user.getAnonId(request.session["privKey"])
                            )

                            memory.setMediaSize(current_user.getPubkey(), request.FILES["media"].size)
                            memory.setLink(current_user.getPubkey(), file[0])
                        except RuntimeError as e:
                            alerts["file"] = prepare_lang["prepare"]["long_texts"]["alerts"]["file_to_big"]
                        except Exception as e:
                            alerts["file"] = prepare_lang["prepare"]["long_texts"]["alerts"]["file_error"]
                    else:
                        alerts["file"] = prepare_lang["prepare"]["long_texts"]["alerts"]["file_to_big"]

                if 'media_text' in request.POST.keys() and not alerts:  # Optional
                    memory.setMediaText(current_user.getPubkey(), request.POST["media_text"])

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

                return HttpResponseRedirect(reverse('prepare:memory'))


            else:  # If no type is entered
                alerts["type"] = prepare_lang["prepare"]["long_texts"]["alerts"]["no_type"]
        else:  # If Title is either empty or too long
            if len(request.POST["title"]) >= 64:
                alerts["title"] = prepare_lang["prepare"]["long_texts"]["alerts"]["title_to_long"]
            else:
                alerts["title"] = prepare_lang["prepare"]["long_texts"]["alerts"]["no_title"]

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


def MemoryView(request):

    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    prepare_lang = get_lang(sections=["prepare"])

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
        "add_memory": prepare_lang["prepare"]["long_texts"]["add_memory"]
    }

    return render(request, 'prepare/memories.html', args)
