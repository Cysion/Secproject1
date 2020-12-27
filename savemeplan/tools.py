from savemeplan.models import SaveMePlan
from login.models import User

from tools.confman import get_lang

import datetime


def top5_options(user, step, symkey):
    """
    Get top 5 most used options on Save.me Plan for user.

    user=The logged in user as User object
    step=The step in Save.me Plan
    symkey=Users AES-key used for decryption in this function

    Returns a list with strings.
    """
    savemeplan_step = SaveMePlan.objects.filter(UserId=user)
    all_options_on_step = dict()  # Key is a option a user have entered and value is frequency

    for savemeplan_item in savemeplan_step:  # Get all matching steps and count frequency
        dec_step = savemeplan_item.getStep(symkey)

        if dec_step == step:
            step_text = savemeplan_item.getText(symkey)

            if step_text in all_options_on_step:
                all_options_on_step[step_text] += 1
            else:
                all_options_on_step[step_text] = 1

    top_5 = []
    for text, freq in all_options_on_step.items():
        if text != 'EMPTY':
            if len(top_5) == 0:
                top_5.append(text)

            else:
                for i in range(len(top_5)):
                    if text not in top_5 and freq > all_options_on_step[top_5[i]]:
                        top_5.insert(i, text)

                if len(top_5) > 5:
                    top_5.pop()

    return top_5

def top_5_bad_good(user, symkey):
    """
    Get top 5 most used good and bad options on Save.me Plan for user.

    user=The logged in user as User object
    symkey=Users AES-key used for decryption in this function

    Returns a list where index 0 is bad list and 1 is good list.
    """
    step = 'B3'
    savemeplan_step = SaveMePlan.objects.filter(UserId=user)
    all_bad_options_on_step = dict()  # Key is a option a user have entered and value is frequency
    all_good_options_on_step = dict()  # Key is a option a user have entered and value is frequency

    for savemeplan_item in savemeplan_step:  # Get all matching steps and count frequency
        dec_step = savemeplan_item.getStep(symkey)

        if dec_step == step:
            step_text = savemeplan_item.getText(symkey)
            dec_text_split = step_text.split(';')
            dec_bad = dec_text_split[0]
            dec_good = dec_text_split[1]

            if dec_bad in all_bad_options_on_step:
                all_bad_options_on_step[dec_bad] += 1
            else:
                all_bad_options_on_step[dec_bad] = 1

            if dec_good in all_good_options_on_step:
                all_good_options_on_step[dec_good] += 1
            else:
                all_good_options_on_step[dec_good] = 1

    top_5_bad = []
    for text, freq in all_bad_options_on_step.items():
        if text != 'EMPTY':
            if len(top_5_bad) == 0:
                top_5_bad.append(text)

            else:
                for i in range(len(top_5_bad)):
                    if (text not in top_5_bad and freq > all_bad_options_on_step[top_5_bad[i]]):
                        top_5_bad.insert(i, text)

                if len(top_5_bad) > 5:
                    top_5_bad.pop()

    top_5_good = []
    for text, freq in all_good_options_on_step.items():
        if text != 'EMPTY':
            if len(top_5_good) == 0:
                top_5_good.append(text)

            else:
                for i in range(len(top_5_good)):
                    if (text not in top_5_good and freq > all_good_options_on_step[top_5_good[i]]):
                        top_5_good.insert(i, text)

                if len(top_5_good) > 5:
                    top_5_good.pop()

    return [top_5_bad, top_5_good]

def extend_top5(top5, default):
    """
    Extend top5 if lenght is lower then 5.

    top5 = result from top5_options function
    default = default/example options

    Return a list with 5 options
    """

    top5_lower = [x.lower() for x in top5]
    top_5_len = len(top5)

    if top_5_len < 5:
        for option in default:
            if top_5_len < 5:
                if option.lower() not in top5_lower:
                    top5.append(option)
                    top_5_len += 1
    return top5

def decrypt_steps(steps, symkey):
    """Decrypts all steps in 'steps'.
    Returns a list with elements as tuples. First element in tuple is id
    and second is decrypted step.

    steps = list with SaveMePlan objects.
    symkey=Users AES-key used for decryption in this function
    """
    dec_steps = []

    for step in steps:
        temp = (step.id, step.getStep(symkey))
        dec_steps.append(temp)

    return dec_steps

def get_savemeplan_items(user, symkey, id=-1, b3_pritty=True):
    """Get all items from savemeplan. Returns a list with step data. Step data
    is a list with values in index order (0) Step, (1) Text and (2) Rating.

    user = User object. The user which Save.Me Plan session which this function
    retrieves.
    symkey = Users AES-key used for decryption in this function.
    id = the Save.me Plan id. If none sent get from the latest item from user.
    b3_pritty = If step B3 should return a more readable string. Instead of
    bad;good it returns 'Replace bad with good'.
    """
    savemeplan_data = []
    if id == -1:
        try:
            id = user.savemeplan_set.order_by('SaveMePlanId').reverse()[0].SaveMePlanId
        except IndexError as e:  # Never done Save Me Plan.
            id = -1

    if id != -1:
        steps = user.savemeplan_set.filter(SaveMePlanId=id)

        for step in steps:
            smp_step = step.getStep(symkey)
            smp_text = step.getText(symkey)
            smp_rating = step.getValue(symkey)

            if b3_pritty and smp_step == 'B3':  # Step B3 will have on the format <bad thing>;<good thing>
                smp_lang = get_lang(sections=['savemeplan'])
                smp_text = f"{smp_lang['savemeplan']['replace']} {smp_text}"
                smp_text = smp_text.replace(';', f" {smp_lang['savemeplan']['with']} ")

            savemeplan_data.append([smp_step, smp_text, smp_rating])

        savemeplan_data.sort(key=lambda x: x[0])  # Sort by step.

    return savemeplan_data

def get_step_data(SaveMePlanId, user, symkey, step):
    """Decrpt data from a step on Save.Me Plan. Returns (text, rating) in tuple.

    SaveMePlanId = Save.Me Plan session id
    user = User object.
    symkey = Users AES-key used for decryption in this function.
    step = which step on Save.Me Plan
    """
    data = ''
    rating = ''
    done_steps = get_savemeplan_items(user, symkey, SaveMePlanId, False)
    for itt_step in done_steps:
        if itt_step[0] == step:
            data = itt_step[1]
            rating = int(itt_step[2])

    return (data, rating)


def get_all_savemeplan_items(user, symkey):
    """Decrypt all Save.Me Plan saved inputs. Returns dictonary where keys are
    Save.Me Plan session ids and value is a second dictonary. The second
    dictonary keys are the step and element is decrypted data. The decrypted
    data is a dictonary with keys
    Key = Save.Me Plan step
    Text = Saved input from user
    Value = saved rating.

    user = User object. The user which all data should be retrieved.
    symkey = Users AES-key used for decryption in this function.
    """
    entries = SaveMePlan.objects.filter(UserId=user)
    pageDict = dict()
    for entry in entries:
        if entry.getId() not in pageDict:
            pageDict[entry.getId()] = dict()
        step = entry.getStep(symkey)

        text = entry.getText(symkey)

        if step == 'B3':  # Step B3 will have on the format <bad thing>;<good thing>
            smp_lang = get_lang(sections=['savemeplan'])
            text = f"{smp_lang['savemeplan']['replace']} {text}"
            text = text.replace(';', f" {smp_lang['savemeplan']['with']} ")

        time = datetime.datetime.fromtimestamp(int(entry.getTime(symkey)))

        pageDict[entry.getId()]['Datetime'] = time.strftime('%d/%m-%Y %H:%S')

        pageDict[entry.getId()][step] = {
            'Key': step,
            'Text': text,
            'Value': entry.getValue(symkey),
        }
    return pageDict


def reencrypt_savemeplan(user, old_symkey, new_symkey):
    """Reencrypts all Save.Me Plan data.

    user = User object. The user which all data should be reencrypted.
    old_symkey = Old AES-key used for decryption in this function.
    new_symkey = New AES-key used for encryption in this function.
    """
    entries = SaveMePlan.objects.filter(UserId=user)
    for entry in entries:
        entry.setStep(new_symkey, entry.getStep(old_symkey))
        entry.setText(new_symkey, entry.getText(old_symkey))
        entry.setValue(new_symkey, entry.getValue(old_symkey))
        entry.setTime(new_symkey, entry.getTime(old_symkey))
        entry.save()
