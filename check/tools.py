import datetime
import login.models
import random

def fillcheck(user, symkey):
    """Fill check table with random data untill current date.

    user = Current User as object
    symkey = Users symetric key. Used for decryption.
    """
    today = datetime.date.today()

    check_entries = user.check_set.all().order_by('CheckId').reverse()
    if len(check_entries) > 0:
        last_entry = check_entries[0]
        last_entry_date = last_entry.getDate()
        print(today)
        print(last_entry_date+datetime.timedelta(days=1))

        while last_entry_date+datetime.timedelta(days=1) < today:
            last_entry_date = last_entry_date+datetime.timedelta(days=1)
            random_data = ''
            for i in range(0,8):
                random_int = random.randrange(1, 100000)
                random_data = random_data+str(random_int)

            last_entry = user.check_set.create(Date=last_entry_date)
            last_entry.setRating(symkey, random_data)
            last_entry.save()
