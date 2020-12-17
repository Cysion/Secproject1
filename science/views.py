from django.shortcuts import render

# Create your views here.



import science.tools




def export_view(request):
    LOGGER = science.tools.get_logger("scienceview")
    one_time_pass = gen_otp().split(":")[1]
    if request.method == 'POST':
        if request.POST["export_key"] == one_time_pass:
            export_data()
        else:
            LOGGER.warning("Wrong export key used!")
    args = {
        'POST': request.POST,
        'form': {
            "export_key":"Enter one time key",
        }
    }
    return render(request, 'science/export.html', args)


