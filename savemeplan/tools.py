from savemeplan.models import SaveMePlan
from login.models import User


def top5_options(user, step, PrivKey):
    """
    Get top 5 most used options on Save.me Plan for user.

    user=The logged in user as User object
    step=The step in Save.me Plan
    PrivKey=Users Private key used for decryption

    Returns a list with strings.
    """
    savemeplan_step = SaveMePlan.objects.filter(UserId=user)
    all_options_on_step = dict()  # Key is a option a user have entered and value is frequency

    for savemeplan_item in savemeplan_step:  # Get all matching steps and count frequency
        dec_step = savemeplan_item.getStep(PrivKey)

        if dec_step == step:
            step_text = savemeplan_item.getText(PrivKey)

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

def top_5_bad_good(user, PrivKey):
    """
    Get top 5 most used good and bad options on Save.me Plan for user.

    user=The logged in user as User object
    PrivKey=Users Private key used for decryption

    Returns a list where index 0 is bad list and 1 is good list.
    """
    step = 'B3'
    savemeplan_step = SaveMePlan.objects.filter(UserId=user)
    all_bad_options_on_step = dict()  # Key is a option a user have entered and value is frequency
    all_good_options_on_step = dict()  # Key is a option a user have entered and value is frequency

    for savemeplan_item in savemeplan_step:  # Get all matching steps and count frequency
        dec_step = savemeplan_item.getStep(PrivKey)

        if dec_step == step:
            step_text = savemeplan_item.getText(PrivKey)
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
