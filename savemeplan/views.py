from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.

from tools.confman import get_lang  # Needed for retrieving text from language file

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

def StartView(request):

    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

    return HttpResponseRedirect(reverse('savemeplan:Step', args=(0,)))  # Redirect user to savemeplan part A

def StepView(request, step):
    if not 'UserId' in request.session.keys():  # This is a check if a user is logged in.
        return HttpResponseRedirect(reverse('login:Login'))

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
        else:
            # Check for stuff and add to db...

            return HttpResponseRedirect(reverse('savemeplan:Step', args=(step+1,)))

    if step == 0:  # Part A

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
        default_options = savemeplan_lang['savemeplan']['long_texts']['sitrate']  #
        content['options'] = default_options

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
        content['options'] = default_options

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
        content['step'] =  savemeplan_lang['savemeplan']['mytho']
        default_options = savemeplan_lang['savemeplan']['long_texts']['thorate']
        content['options'] = default_options

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
        content['step'] =  savemeplan_lang['savemeplan']['mybeh']
        default_options = savemeplan_lang['savemeplan']['long_texts']['emorate']
        content['options'] = default_options

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
        content['step'] =  savemeplan_lang['savemeplan']['calm_step']
        default_options = savemeplan_lang['savemeplan']['long_texts']['calrate']
        content['options'] = default_options

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
        content['step'] =  savemeplan_lang['savemeplan']['my_route']
        default_options = savemeplan_lang['savemeplan']['long_texts']['rourate']
        content['options'] = default_options

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
        content['step'] =  savemeplan_lang['savemeplan']['repltitle']

        default_bad =  savemeplan_lang['savemeplan']['long_texts']['repbad']
        default_good = savemeplan_lang['savemeplan']['long_texts']['repgood']
        content['options'] = list()

        if len(default_bad) <= len(default_good):  # Add good and bad in examples in raplace
            for i in range(len(default_bad)):
                content['options'].append((default_bad[i], default_good[i]))
        else:
            for i in range(len(default_good)):
                content['options'].append((default_bad[i], default_good[i]))

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
        content['options'] = default_options

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
        contacts = [{
            'name': 'Kevin Engström',
            'number': '0701234567'
        }, {
            'name': 'Robin Källström',
            'number': '0701234567'
        }]
        content['contacts_list'] = contacts

        content['code_red'] = savemeplan_lang['savemeplan']['codered'].upper()
        content['code_orange'] = savemeplan_lang['savemeplan']['codeor'].upper()
        content['code_yellow'] = savemeplan_lang['savemeplan']['codeyel'].upper()
        content['code_blue'] = savemeplan_lang['savemeplan']['codeblue'].upper()
        content['code_green'] = savemeplan_lang['savemeplan']['codegre'] .upper()

        content['contacts'] = savemeplan_lang['savemeplan']['contacts']  # Word contacts
        content['message'] = savemeplan_lang['savemeplan']['long_texts']['messages']  # Code texts
        content['chat'] = savemeplan_lang['savemeplan']['long_texts']['chat']  # word chat
        content['chat_website'] = savemeplan_lang['savemeplan']['chat_site']

        # Colors on part title and descibe parts.
        content['step_bg'] = STEP_COLORS['C1']

    elif step == 12:  # Step C2

        template = 'savemeplan/step_call.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][11]}"
        content['part'] = 'C'

        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][2]} - {savemeplan_lang['savemeplan']['callhelper']}"
        contacts = [{
            'name': 'Kevin Engström',
            'number': '0701234567'
        }, {
            'name': 'Robin Källström',
            'number': '0701234567'
        }]
        content['contacts_list'] = contacts

        content['step_bg'] = STEP_COLORS['C2']

    elif step == 13:  # Step C3

        template = 'savemeplan/step_gosafe.html'
        title = f"{title} - {savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][11]}"
        content['part'] = 'C'

        content['step_title'] = f"{savemeplan_lang['savemeplan']['steps'][0].upper()} {savemeplan_lang['savemeplan']['steps'][11]} - {savemeplan_lang['savemeplan']['safe']}"
        content['step'] =  savemeplan_lang['savemeplan']['go_to_safe']
        default_options = savemeplan_lang['savemeplan']['long_texts']['safe']
        content['options'] = default_options

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

        content['step_title'] = savemeplan_lang['savemeplan']['summary']

        content['colors'] = STEP_COLORS

    args = {
        'menu_titles': UNIVERSAL_LANG["universal"]["titles"],  # This is the menu-titles text retrieved from language file.,
        'title': title,
        'content': content,
        'next_step': next_step,
        'back': UNIVERSAL_LANG['universal']['back']
    }

    return render(request, template, args)
