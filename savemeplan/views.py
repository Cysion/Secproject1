from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
# Create your views here.

from tools.confman import get_lang  # Needed for retrieving text from language file
from savemeplan.models import SaveMePlan, Contacts
from login.models import User
import tools.global_alerts
from science.tools import new_entry
import time
import savemeplan.tools
import mimetypes
import prepare.tools

UNIVERSAL_LANG = get_lang(sections=["universal"])  # Needed to get universal lang texts.

STEP_COLORS = {  # Main color for that step.
    'A1': '#f77979',
    'A2': '#ff9cf2',
    'A3': '#cfcfcf',
    'A4': '#f7c074',
    'B1': '#c2904e',
    'B2': '#8bff87',
    'B3': '#adf8ff',
    'B4': '#88b9eb',
    'C1': '#50cc68',
    'C2': '#5f85d9',
    'C3': '#52e8ff',
    'C4': '#ff4040',
}

def start_view(request):
    """Redirect to step_view with step=0"""
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    return HttpResponseRedirect(reverse('savemeplan:Step', args=(0,)))  # Redirect user to savemeplan part A

def step_view(request, step):
    """Main Save.me Plan view. Handles all interfaces and saving to database for each step.

    step=Current step, is between 0-15. 0, 5, 10, 15 is Part A, B, C, D
    And those between is the actual steps for Save.me Plan ex 1=A1, 7=B2...
    """
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))
    elif request.session["Role"] != "User":
        return HttpResponseRedirect(reverse('userprofile:Profile'))

    prepare.tools.delete_temp_files(request.session)

    user = User.objects.filter(pk=request.session['UserId'])[0]
    symkey = user.getSymKey(request.session['PrivKey'])

    savemeplan_lang = get_lang(sections=['savemeplan'])
    template = ''  # Diffrent step sets diffrent template
    content = {  # Main variable for each step content
        'describe_info': savemeplan_lang['savemeplan']['long_texts']['describe_info'],
        'current_step': step
    }
    title = savemeplan_lang['savemeplan']['title']
    next_step = savemeplan_lang['savemeplan']['next_step']

    if step not in range(0, 17):  # If someone enters a non existing step
        step = 0

    if request.POST:
        if 'choosen_item' in request.POST.keys():
            content["textarea_text"] = request.POST['choosen_item']
        else:  # User is going to next step.
            steps = {
                1: 'A1',
                2: 'A2',
                3: 'A3',
                4: 'A4',
                6: 'B1',
                7: 'B2',
                8: 'B3',
                9: 'B4',
                11: 'C1',
                12: 'C2',
                13: 'C3',
                14: 'C4',
            }
            if 'SaveMePlanId' not in request.session.keys():

                last_savemeplan = user.savemeplan_set.order_by('SaveMePlanId').reverse()
                if len(last_savemeplan) != 0:
                    request.session['SaveMePlanId'] = last_savemeplan[0].SaveMePlanId+1  # Increase SaveMePlanId with one.
                else:
                    request.session['SaveMePlanId'] = 0

            current_smp_session = user.savemeplan_set.filter(SaveMePlanId=request.session['SaveMePlanId'])
            done_steps = savemeplan.tools.decrypt_steps(current_smp_session, symkey)

            found_id = -1
            for item in done_steps:
                if item[1] == steps[step]:
                    found_id = item[0]

            if found_id == -1:
                savemeplan_step = SaveMePlan(SaveMePlanId=request.session['SaveMePlanId'], UserId=user)
            else:  # User is changing on a previously saved step
                savemeplan_step = SaveMePlan.objects.filter(pk=found_id)[0]

            if step in [1, 2, 3, 4, 6, 7, 9]:  # Is using step_default.html template
                if len(request.POST['describe']) != 0:
                    if found_id == -1:
                        savemeplan_step.setStep(symkey, steps[step])  # Save step as a user reads it

                    if 'describe' in request.POST.keys():
                        if len(request.POST['describe']) != 0:
                            if len(request.POST['describe']) <= 64:
                                savemeplan_step.setText(symkey,request.POST['describe'])
                            else:
                                savemeplan_step.setText(symkey, request.POST['describe'][:64])
                                tools.global_alerts.add_alert(request, 'warning', UNIVERSAL_LANG['universal']['warning'], savemeplan_lang['savemeplan']['long_texts']['text_to_long'])
                        elif found_id == -1:
                            savemeplan_step.setText(symkey, 'EMPTY')
                    elif found_id == -1:
                        savemeplan_step.setText(symkey, 'EMPTY')

                    if 'rating' in request.POST.keys():
                        if len(request.POST['rating']) != 0:
                            savemeplan_step.setValue(symkey, request.POST['rating'])
                        elif found_id == -1:
                            savemeplan_step.setValue(symkey, '-1')
                    elif found_id == -1:
                        savemeplan_step.setValue(symkey, '-1')

                    savemeplan_step.setTime(symkey, str(int(time.time())))

                    savemeplan_step.save()
                elif found_id != -1:
                    savemeplan_step.delete()

            elif step == 8:  # Replace a bad thing with a good thing step.
                if 'bad' and 'good' in request.POST.keys():

                    if (((request.POST['bad'] == 'bad_other'
                        and len(request.POST['bad_other']) != 0)
                        and (request.POST['good'] == 'good_other'
                        and len(request.POST['good_other']) != 0))
                        or request.POST['bad'] != 'bad_other'
                        or request.POST['good'] != 'good_other'):
                        if found_id == -1:
                            savemeplan_step.setStep(symkey, steps[step])  # Save step as a user reads it

                        replace = ''  # Will have format <bad>;<good> IF one of them is empty they will be replaced by EMPTY

                        if 'bad' in request.POST.keys():
                            if request.POST['bad'] != 'other':
                                if len(request.POST['bad']) <= 64:
                                    replace = f"{request.POST['bad']};"
                                else:
                                    replace = f"{request.POST['bad'][:64]};"
                                    tools.global_alerts.add_alert(request, 'warning', UNIVERSAL_LANG['universal']['warning'], savemeplan_lang['savemeplan']['long_texts']['text_to_long'])

                            else:
                                if len(request.POST['bad_other']) != 0:
                                    if len(request.POST['bad_other']) <= 64:
                                        replace = f"{request.POST['bad_other']};"
                                    else:
                                        replace = f"{request.POST['bad_other'][:64]};"
                                        tools.global_alerts.add_alert(request, 'warning', UNIVERSAL_LANG['universal']['warning'], savemeplan_lang['savemeplan']['long_texts']['text_to_long'])

                                else:
                                    replace = 'EMPTY;'
                        else:
                            replace = 'EMPTY;'

                        if 'good' in request.POST.keys():
                            if request.POST['good'] != 'other':
                                if len(request.POST['good']) <= 64:
                                    replace = f"{replace}{request.POST['good']}"
                                else:
                                    replace = f"{request.POST['good'][:64]};"
                                    tools.global_alerts.add_alert(request, 'warning', UNIVERSAL_LANG['universal']['warning'], savemeplan_lang['savemeplan']['long_texts']['text_to_long'])

                            else:
                                if len(request.POST['good_other']) != 0:
                                    if len(request.POST['good_other']) <= 64:
                                        replace = f"{replace}{request.POST['good_other']}"
                                    else:
                                        replace = f"{request.POST['good_other'][:64]};"
                                        tools.global_alerts.add_alert(request, 'warning', UNIVERSAL_LANG['universal']['warning'], savemeplan_lang['savemeplan']['long_texts']['text_to_long'])
                                else:
                                    replace = f"{replace}EMPTY"

                        else:
                            replace = f"{replace}EMPTY"
                        if replace != 'EMPTY;EMPTY':
                            savemeplan_step.setText(symkey, replace)
                            savemeplan_step.setValue(symkey, '-1')
                            savemeplan_step.setTime(symkey, str(int(time.time())))
                            savemeplan_step.save()
                    elif found_id != -1:
                        savemeplan_step.delete()
                elif found_id != -1:
                    savemeplan_step.delete()

            elif step == 13:  # Go to a safe place step
                if ('place' in request.POST.keys()
                    and (request.POST['place'] != 'other'
                    or (request.POST['place'] == 'other'
                    and len(request.POST['place_other']) != 0))):
                    if found_id == -1:
                        savemeplan_step.setStep(symkey, steps[step])  # Save step as a user reads it

                    goto = ''

                    if 'place' in request.POST.keys():
                        if request.POST['place'] != 'other':
                            goto = request.POST['place']

                        else:
                            if len(request.POST['place_other']) != 0:
                                goto = request.POST['place_other']
                            else:
                                goto = 'EMPTY'

                    else:
                        goto = 'EMPTY'

                    if found_id == -1:
                        if len(goto) <= 64:
                            savemeplan_step.setText(symkey, goto)
                        else:
                            savemeplan_step.setText(symkey, goto[:64])
                            tools.global_alerts.add_alert(request, 'warning', UNIVERSAL_LANG['universal']['warning'], savemeplan_lang['savemeplan']['long_texts']['text_to_long'])

                    savemeplan_step.setValue(symkey, '-1')
                    savemeplan_step.setTime(symkey, str(int(time.time())))

                    savemeplan_step.save()
                elif found_id != -1:
                    savemeplan_step.delete()

            return HttpResponseRedirect(reverse('savemeplan:Step', args=(step+1,)))

    if step == 0:  # Part A
        new_entry("g1", user.getAnonId(request.session['PrivKey']), f"save", role=request.session['Role'])

        template = 'savemeplan/part.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['part'].upper()} {savemeplan_lang['savemeplan']['parts'][0]}"  # Tab title
        content['title'] = f"{savemeplan_lang['savemeplan']['part'].upper()} {savemeplan_lang['savemeplan']['parts'][0]}: {savemeplan_lang['savemeplan']['part_a']}"
        content['part'] = 'A'

        content['step_1'] = (1, f"{savemeplan_lang['savemeplan']['steps'][0]} {savemeplan_lang['savemeplan']['steps'][1]}: {savemeplan_lang['savemeplan']['mysit'].upper()}", STEP_COLORS['A1'])
        content['step_2'] = (2, f"{savemeplan_lang['savemeplan']['steps'][0]} {savemeplan_lang['savemeplan']['steps'][2]}: {savemeplan_lang['savemeplan']['myemo'].upper()}", STEP_COLORS['A2'])
        content['step_3'] = (3, f"{savemeplan_lang['savemeplan']['steps'][0]} {savemeplan_lang['savemeplan']['steps'][3]}: {savemeplan_lang['savemeplan']['mytho'].upper()}", STEP_COLORS['A3'])
        content['step_4'] = (4, f"{savemeplan_lang['savemeplan']['steps'][0]} {savemeplan_lang['savemeplan']['steps'][4]}: {savemeplan_lang['savemeplan']['mybeh'].upper()}", STEP_COLORS['A4'])

    elif step == 1:  # Step A1

        template = 'savemeplan/step_default.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][1]}"
        content['part'] = 'A'

        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][1]} - {savemeplan_lang['savemeplan']['long_texts']['steps'][0]}"
        content['step'] =  savemeplan_lang['savemeplan']['mysit']

        default_options = savemeplan_lang['savemeplan']['long_texts']['sitrate']
        top_5 = savemeplan.tools.top5_options(user, 'A1', symkey)  # Get most used options
        if len(top_5) < 5:
            top_5 = savemeplan.tools.extend_top5(top_5, default_options)
        content['options'] = top_5

        if 'SaveMePlanId' in request.session.keys():
            content['data'] = savemeplan.tools.get_step_data(request.session['SaveMePlanId'], user, symkey, 'A1')

        content['describe_placeholder'] = savemeplan_lang['savemeplan']['sittext']
        content['rate'] = savemeplan_lang['savemeplan']['rate_sit']  # Rating text
        content['1'] = savemeplan_lang['savemeplan']['unbearable']  # Rating 1 text
        content['9'] = savemeplan_lang['savemeplan']['nomild']  # Rating 9 text

        content['step_bg'] = STEP_COLORS['A1']  # Colors on title box and step part

    elif step == 2:  # Step A2

        template = 'savemeplan/step_default.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][2]}"
        content['part'] = 'A'

        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][2]} - {savemeplan_lang['savemeplan']['long_texts']['steps'][0]}"
        content['step'] =  savemeplan_lang['savemeplan']['myemo']

        default_options = savemeplan_lang['savemeplan']['long_texts']['emorate']
        top_5 = savemeplan.tools.top5_options(user, 'A2', symkey)  # Get most used options
        if len(top_5) < 5:
            top_5 = savemeplan.tools.extend_top5(top_5, default_options)
        content['options'] = top_5

        if 'SaveMePlanId' in request.session.keys():
            content['data'] = savemeplan.tools.get_step_data(request.session['SaveMePlanId'], user, symkey, 'A2')

        content['describe_placeholder'] = savemeplan_lang['savemeplan']['emotext']
        content['rate'] = savemeplan_lang['savemeplan']['rate_emo']  # Rating text
        content['1'] = savemeplan_lang['savemeplan']['unbearable']  # Rating 1 text
        content['9'] = savemeplan_lang['savemeplan']['nomild']  # Rating 9 text

        content['step_bg'] = STEP_COLORS['A2']  # Colors on title box and step part

    elif step == 3:  # Step A3

        template = 'savemeplan/step_default.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][3]}"
        content['part'] = 'A'

        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][3]} - {savemeplan_lang['savemeplan']['long_texts']['steps'][0]}"
        content['step'] = savemeplan_lang['savemeplan']['mytho']

        default_options = savemeplan_lang['savemeplan']['long_texts']['thorate']
        top_5 = savemeplan.tools.top5_options(user, 'A3', symkey)  # Get most used options
        if len(top_5) < 5:
            top_5 = savemeplan.tools.extend_top5(top_5, default_options)
        content['options'] = top_5

        if 'SaveMePlanId' in request.session.keys():
            content['data'] = savemeplan.tools.get_step_data(request.session['SaveMePlanId'], user, symkey, 'A3')

        content['describe_placeholder'] = savemeplan_lang['savemeplan']['thotext']
        content['rate'] = savemeplan_lang['savemeplan']['rate_tho']
        content['1'] = savemeplan_lang['savemeplan']['unbearable']
        content['9'] = savemeplan_lang['savemeplan']['nomild']

        content['step_bg'] = STEP_COLORS['A3']

    elif step == 4:  # Step a 4
        template = 'savemeplan/step_default.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][4]}"
        content['part'] = 'A'

        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][4]} - {savemeplan_lang['savemeplan']['long_texts']['steps'][0]}"
        content['step'] = savemeplan_lang['savemeplan']['mybeh']

        default_options = savemeplan_lang['savemeplan']['long_texts']['emorate']
        top_5 = savemeplan.tools.top5_options(user, 'A4', symkey)  # Get most used options
        if len(top_5) < 5:
            top_5 = savemeplan.tools.extend_top5(top_5, default_options)
        content['options'] = top_5

        if 'SaveMePlanId' in request.session.keys():
            content['data'] = savemeplan.tools.get_step_data(request.session['SaveMePlanId'], user, symkey, 'A4')

        content['describe_placeholder'] = savemeplan_lang['savemeplan']['emotext']
        content['rate'] = savemeplan_lang['savemeplan']['rate_beh']
        content['1'] = savemeplan_lang['savemeplan']['unbearable']
        content['9'] = savemeplan_lang['savemeplan']['nomild']

        content['step_bg'] = STEP_COLORS['A4']

    elif step == 5:  # Part B

        template = 'savemeplan/part.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['part'].upper()} {savemeplan_lang['savemeplan']['parts'][1]}"
        content['part'] = 'B'

        content['title'] = f"{savemeplan_lang['savemeplan']['part'].upper()} {savemeplan_lang['savemeplan']['parts'][1]}: {savemeplan_lang['savemeplan']['part_b']}"
        content['step_1'] = (6, f"{savemeplan_lang['savemeplan']['steps'][0]} {savemeplan_lang['savemeplan']['steps'][5]}: {savemeplan_lang['savemeplan']['calm'].upper()}", STEP_COLORS['B1'])
        content['step_2'] = (7, f"{savemeplan_lang['savemeplan']['steps'][0]} {savemeplan_lang['savemeplan']['steps'][6]}: {savemeplan_lang['savemeplan']['rout'].upper()}", STEP_COLORS['B2'])
        content['step_3'] = (8, f"{savemeplan_lang['savemeplan']['steps'][0]} {savemeplan_lang['savemeplan']['steps'][7]}: {savemeplan_lang['savemeplan']['repl'].upper()}", STEP_COLORS['B3'])
        content['step_4'] = (9, f"{savemeplan_lang['savemeplan']['steps'][0]} {savemeplan_lang['savemeplan']['steps'][8]}: {savemeplan_lang['savemeplan']['prot'].upper()}", STEP_COLORS['B4'])


    elif step == 6:  # Step B1

        template = 'savemeplan/step_default.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][5]}"
        content['part'] = 'B'

        default_options = savemeplan_lang['savemeplan']['long_texts']['calrate']
        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][5]} - {savemeplan_lang['savemeplan']['calmtitle'].upper()}"
        content['step'] = savemeplan_lang['savemeplan']['calm_step']

        default_options = savemeplan_lang['savemeplan']['long_texts']['calrate']
        top_5 = savemeplan.tools.top5_options(user, 'B1', symkey)  # Get most used options
        if len(top_5) < 5:
            top_5 = savemeplan.tools.extend_top5(top_5, default_options)
        content['options'] = top_5

        if 'SaveMePlanId' in request.session.keys():
            content['data'] = savemeplan.tools.get_step_data(request.session['SaveMePlanId'], user, symkey, 'B1')

        content['describe_placeholder'] = savemeplan_lang['savemeplan']['calmtext']
        content['rate'] = savemeplan_lang['savemeplan']['rate_calm']
        content['1'] = savemeplan_lang['savemeplan']['unbearable']
        content['9'] = savemeplan_lang['savemeplan']['nomild']

        content['step_bg'] = STEP_COLORS['B1']

    elif step == 7:  # Step B2
        template = 'savemeplan/step_default.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][6]}"
        content['part'] = 'B'

        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][6]} - {savemeplan_lang['savemeplan']['routtitle'].upper()}"
        content['step'] = savemeplan_lang['savemeplan']['my_route']

        default_options = savemeplan_lang['savemeplan']['long_texts']['rourate']
        top_5 = savemeplan.tools.top5_options(user, 'B2', symkey)  # Get most used options
        if len(top_5) < 5:
            top_5 = savemeplan.tools.extend_top5(top_5, default_options)
        content['options'] = top_5

        if 'SaveMePlanId' in request.session.keys():
            content['data'] = savemeplan.tools.get_step_data(request.session['SaveMePlanId'], user, symkey, 'B2')

        content['describe_placeholder'] = savemeplan_lang['savemeplan']['routtext']
        content['rate'] = savemeplan_lang['savemeplan']['rate_rout']
        content['1'] = savemeplan_lang['savemeplan']['yes']
        content['4'] = savemeplan_lang['savemeplan']['no']

        content['step_bg'] = STEP_COLORS['B2']

    elif step == 8:  # Step B3

        template = 'savemeplan/step_replace.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][7]}"
        content['part'] = 'B'

        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][3]} - {savemeplan_lang['savemeplan']['repltitle']}"
        content['step'] = savemeplan_lang['savemeplan']['repltitle']

        default_bad = savemeplan_lang['savemeplan']['long_texts']['repbad']
        default_good = savemeplan_lang['savemeplan']['long_texts']['repgood']
        top_5 = savemeplan.tools.top_5_bad_good(user, symkey)
        content['options'] = list()

        if 'SaveMePlanId' in request.session.keys():
            text = savemeplan.tools.get_step_data(request.session['SaveMePlanId'], user, symkey, 'B3')[0].split(';')
            if len(text) == 2:
                content['text_bad'] = text[0]
                content['text_good'] = text[1]

        if len(top_5[0]) < 5:
            top_5[0] = savemeplan.tools.extend_top5(top_5[0], default_bad)

        if len(top_5[1]) < 5:
            top_5[1] = savemeplan.tools.extend_top5(top_5[1], default_good)

        for i in range(len(top_5[0])):
            content['options'].append((top_5[0][i], top_5[1][i]))

        content['dangerous'] = savemeplan_lang['savemeplan']['put_away']
        content['good'] = savemeplan_lang['savemeplan']['find_safe']
        content['other'] = savemeplan_lang['savemeplan']['other']
        content['other_placeholder'] = savemeplan_lang['savemeplan']['repladd']

        content['step_bg'] = STEP_COLORS['B3']

    elif step == 9:  # Step B4

        template = 'savemeplan/step_default.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][8]}"
        content['part'] = 'B'

        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][4]} - {savemeplan_lang['savemeplan']['prot_title']}"
        content['step'] =  savemeplan_lang['savemeplan']['my_values']

        default_options = savemeplan_lang['savemeplan']['long_texts']['protect']
        top_5 = savemeplan.tools.top5_options(user, 'B4', symkey)  # Get most used options
        if len(top_5) < 5:
            top_5 = savemeplan.tools.extend_top5(top_5, default_options)
        content['options'] = top_5

        if 'SaveMePlanId' in request.session.keys():  # Check if user allready submittet a value.
            content['data'] = savemeplan.tools.get_step_data(request.session['SaveMePlanId'], user, symkey, 'B4')

        content['describe_placeholder'] = savemeplan_lang['savemeplan']['name_values']
        content['rate'] = savemeplan_lang['savemeplan']['rate_values']
        content['1'] = '0 %'
        content['9'] = '100 %'

        # Colors on part title and descibe parts.
        content['step_bg'] = STEP_COLORS['B4']

    elif step == 10:  # Part C

        template = 'savemeplan/part.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['part'].upper()} {savemeplan_lang['savemeplan']['parts'][2]}"
        content['part'] = 'C'

        content['title'] = f"{savemeplan_lang['savemeplan']['part'].upper()} {savemeplan_lang['savemeplan']['parts'][2]}: {savemeplan_lang['savemeplan']['part_c']}"
        content['step_1'] = (11, f"{savemeplan_lang['savemeplan']['steps'][0]} {savemeplan_lang['savemeplan']['steps'][9]}: {savemeplan_lang['savemeplan']['smsto'].upper()}", STEP_COLORS['C1'])
        content['step_2'] = (12, f"{savemeplan_lang['savemeplan']['steps'][0]} {savemeplan_lang['savemeplan']['steps'][10]}: {savemeplan_lang['savemeplan']['call'].upper()}", STEP_COLORS['C2'])
        content['step_3'] = (13, f"{savemeplan_lang['savemeplan']['steps'][0]} {savemeplan_lang['savemeplan']['steps'][11]}: {savemeplan_lang['savemeplan']['gosafe'].upper()}", STEP_COLORS['C3'])
        content['step_4'] = (14, f"{savemeplan_lang['savemeplan']['steps'][0]} {savemeplan_lang['savemeplan']['steps'][12]}: {savemeplan_lang['savemeplan']['indanger'].upper()} {UNIVERSAL_LANG['universal']['emergency_number']}", STEP_COLORS['C4'])

    elif step == 11:  # Step C1

        template = 'savemeplan/step_message.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][9]}"
        content['part'] = 'C'

        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][9]} - {savemeplan_lang['savemeplan']['sms_chat']}"

        all_contacts_enc = user.contacts_set.all()
        all_contacts_dec = []

        for contact in all_contacts_enc:
            name = contact.getName(request.session['PrivKey'])
            nr = contact.getPhonenumber(request.session['PrivKey'])
            available = contact.getAvailable(request.session['PrivKey'])
            all_contacts_dec.append(
                {
                    'name': name,
                    'number': nr,
                    'available': available
                }
            )


        content['contacts_list'] = all_contacts_dec

        content['code_red'] = savemeplan_lang['savemeplan']['codered'].upper()
        content['code_orange'] = savemeplan_lang['savemeplan']['codeor'].upper()
        content['code_yellow'] = savemeplan_lang['savemeplan']['codeyel'].upper()
        content['code_blue'] = savemeplan_lang['savemeplan']['codeblue'].upper()
        content['code_green'] = savemeplan_lang['savemeplan']['codegre'] .upper()

        content['contacts'] = savemeplan_lang['savemeplan']['contacts']  # Word contacts
        content['message'] = savemeplan_lang['savemeplan']['long_texts']['messages']  # Code texts
        content['chat'] = savemeplan_lang['savemeplan']['long_texts']['chat']  # word chat
        content['chat_website'] = savemeplan_lang['savemeplan']['chat_site']
        content['available'] = savemeplan_lang['savemeplan']['available']

        # Colors on part title and descibe parts.
        content['step_bg'] = STEP_COLORS['C1']

    elif step == 12:  # Step C2

        template = 'savemeplan/step_call.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][11]}"
        content['part'] = 'C'

        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][2]} - {savemeplan_lang['savemeplan']['callhelper']}"

        all_contacts_enc = user.contacts_set.all()
        all_contacts_dec = []

        for contact in all_contacts_enc:
            name = contact.getName(request.session['PrivKey'])
            nr = contact.getPhonenumber(request.session['PrivKey'])
            available = contact.getAvailable(request.session['PrivKey'])
            all_contacts_dec.append(
                {
                    'name': name,
                    'number': nr,
                    'available': available
                }
            )

        content['contacts_list'] = all_contacts_dec
        content['available'] = savemeplan_lang['savemeplan']['available']

        content['step_bg'] = STEP_COLORS['C2']

    elif step == 13:  # Step C3

        template = 'savemeplan/step_gosafe.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][11]}"
        content['part'] = 'C'

        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][11]} - {savemeplan_lang['savemeplan']['safe']}"
        content['step'] =  savemeplan_lang['savemeplan']['go_to_safe']

        default_options = savemeplan_lang['savemeplan']['long_texts']['safe']
        top_5 = savemeplan.tools.top5_options(user, 'C3', symkey)  # Get most used options
        if len(top_5) < 5:
            top_5 = savemeplan.tools.extend_top5(top_5, default_options)
        content['options'] = top_5

        if 'SaveMePlanId' in request.session.keys():
            content['data'] = savemeplan.tools.get_step_data(request.session['SaveMePlanId'], user, symkey, 'C3')

        content['other_placeholder'] = savemeplan_lang['savemeplan']['add_safe']
        content['other'] = savemeplan_lang['savemeplan']['other']
        content['describe_placeholder'] = savemeplan_lang['savemeplan']['thotext']

        content['step_bg'] = STEP_COLORS['C3']

    elif step == 14:  # Step C4

        template = 'savemeplan/step_sos.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][12]}"
        content['part'] = 'C'

        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][12]} - {savemeplan_lang['savemeplan']['if_danger']}"
        content['step'] =  savemeplan_lang['savemeplan']['cant_talk']

        content['sos_1'] = savemeplan_lang['savemeplan']['sos_1']
        content['sos_2'] = savemeplan_lang['savemeplan']['sos_2']
        content['sos_3'] = savemeplan_lang['savemeplan']['sos_3']

        content['call'] = savemeplan_lang['savemeplan']['call_sos']
        content['repeat'] = savemeplan_lang['savemeplan']['repeat_smp']
        content['emergency_nr'] = UNIVERSAL_LANG['universal']['emergency_number']

        # Colors on part title and descibe parts.
        content['step_bg'] = STEP_COLORS['C4']

    elif step == 15:  # Summary
        template = 'savemeplan/step_summary.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['part'].upper()} {savemeplan_lang['savemeplan']['parts'][3]}"
        content['part'] = 'D'

        STEP_TITLES = {
            'A1': savemeplan_lang['savemeplan']['mysit'],
            'A2': savemeplan_lang['savemeplan']['myemo'],
            'A3': savemeplan_lang['savemeplan']['mytho'],
            'A4': savemeplan_lang['savemeplan']['mybeh'],
            'B1': savemeplan_lang['savemeplan']['calm'],
            'B2': savemeplan_lang['savemeplan']['rout'],
            'B3': savemeplan_lang['savemeplan']['repl'],
            'B4': savemeplan_lang['savemeplan']['prot'],
            'C3': savemeplan_lang['savemeplan']['gosafe'],
        }

        content['step_title'] = savemeplan_lang['savemeplan']['summary']
        content['download'] = savemeplan_lang['savemeplan']['download']

        if 'SaveMePlanId' in request.session.keys():
            content['steps'] = savemeplan.tools.get_savemeplan_items(user, symkey, request.session['SaveMePlanId'])
            del request.session['SaveMePlanId']  # User is now done with this session.
        else:
            content['old'] = savemeplan_lang['savemeplan']['long_texts']['old_session']
            content['steps'] = savemeplan.tools.get_savemeplan_items(user, symkey)
            content['rating'] = savemeplan_lang['savemeplan']['rating']

        for smp_step in content['steps']:
            smp_step.append(STEP_COLORS[smp_step[0]])
            smp_step.append(STEP_TITLES[smp_step[0]])

    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.,
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'title': title,
        'content': content,
        'next_step': next_step,
        'back': UNIVERSAL_LANG['universal']['back']
    }
    new_entry("s3", user.getAnonId(request.session['PrivKey']), f"step {step}", role=request.session['Role'])
    return render(request, template, args)

def history_view(request):
    """Diplay a users Save.Me Plan history"""
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))
    elif request.session["Role"] != "User":
        return HttpResponseRedirect(reverse('userprofile:Profile'))

    savemeplan_lang = get_lang(sections=['savemeplan'])

    STEP_COLORS = {  # Main color for that step.
        'A1': '#f77979',
        'A2': '#ff9cf2',
        'A3': '#cfcfcf',
        'A4': '#f7c074',
        'B1': '#c2904e',
        'B2': '#8bff87',
        'B3': '#adf8ff',
        'B4': '#88b9eb',
        'C1': '#50cc68',
        'C2': '#5f85d9',
        'C3': '#52e8ff',
        'C4': '#ff4040',
    }

    STEP_TITLES = {
        'A1': savemeplan_lang['savemeplan']['mysit'],
        'A2': savemeplan_lang['savemeplan']['myemo'],
        'A3': savemeplan_lang['savemeplan']['mytho'],
        'A4': savemeplan_lang['savemeplan']['mybeh'],
        'B1': savemeplan_lang['savemeplan']['calm'],
        'B2': savemeplan_lang['savemeplan']['rout'],
        'B3': savemeplan_lang['savemeplan']['repl'],
        'B4': savemeplan_lang['savemeplan']['prot'],
        'C3': savemeplan_lang['savemeplan']['gosafe'],
    }

    prepare.tools.delete_temp_files(request.session)

    title = savemeplan_lang['savemeplan']['title']

    user = User.objects.filter(pk=request.session['UserId'])[0]
    symkey = user.getSymKey(request.session['PrivKey'])
    global_alerts = []  # The variable which is sent to template
    if "global_alerts" in request.session.keys():  # Check if there is global alerts
        global_alerts = request.session["global_alerts"]  # Retrive global alerts.
        request.session["global_alerts"] = []  # Reset

    entries = savemeplan.tools.get_all_savemeplan_items(user, symkey)

    for session in entries.values():
        for key, step in session.items():
            if key != 'Datetime':
                step['Color'] = STEP_COLORS[step['Key']]
                step['Title'] = STEP_TITLES[step['Key']]
    entries['part'] = 'history'
    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.
        'global_alerts': global_alerts,  # Sending the alerts to template.
        'content': entries,
        'title': title,
        'template': 'base.html',
        'history': savemeplan_lang['savemeplan']['history'],
        'rating': savemeplan_lang['savemeplan']['rating']
    }

    return render(request, 'savemeplan/savemeplan_history.html', args)

def download_contract_view(request):
    """Download a empty contract."""
    fl_path = 'media/save.me_agreement.pdf'
    filename = 'save.me_agreement.pdf'

    fl = open(fl_path, 'rb')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
