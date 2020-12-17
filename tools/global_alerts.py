def add_alert(request, color, title, message, link=None):
    """Add a global alert to current session.

    request = the request variable containing session sent from django.
    color = either success (green), warning (yellow), danger (red), info (blue)
    title = Text in bold before message. Should be Success, Warning or Error.
    message = message itself.
    """
    try:
        alert = {
            "color": color,
            "title": title,
            "message": message,
            "link": link
        }

        if "global_alerts" not in request.session.keys():  # Check if global_elerts is in session allready.
            request.session["global_alerts"] = [alert]
        else:
            request.session["global_alerts"].append(alert)
            request.session.modified = True
        return 1
    except Exception as e:
        return 0

def retrive_alerts(request, amount=-1):
    """
    Retrive global alerts.
    request = the request variable containing session sent from django.
    amount = the amount of global alerts which should be retrieved. Where -1 = all.
    Defaults to -1.

    returns a list of notifications where each element is a dictonary.
    """
    print(amount)
    notifications = []
    if "global_alerts" in request.session.keys():
        while len(request.session["global_alerts"]) > 0 and (amount != 0 or amount == -1):
            notifications.append(request.session["global_alerts"].pop(0))
            if amount != -1:
                amount = amount - 1

    return notifications
