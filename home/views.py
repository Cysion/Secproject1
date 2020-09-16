from django.shortcuts import render
from django.views import generic
# Create your views here.

from django.shortcuts import render

def IndexView(request):
    return render(request, 'home/index.html')
