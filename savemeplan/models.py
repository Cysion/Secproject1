from django.db import models
from login.models import User

# Create your models here.

class SaveMePlan(models.Model):
    """
    Save.Me plan data.

    Step: the plan step.
    Value: Rating between either 0-9 or 0-4 deppending on step.
    Time: Used be researcher
    """

    SaveMePlanId = models.IntegerField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Step = models.CharField(max_length=2, blank=False)
    Text = models.CharField(max_length=120)
    Value = models.IntegerField(blank=False)
    Time = models.DateTimeField(auto_now=True)

class Contacts(models.Model):
    """
    Available contacts for the user.
    Storing information such as Contact name, their phone number and
    when they are available.
    """

    ContactsId = models.IntegerField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Name = models.CharField(max_length=120)
    Phonenumber = models.CharField(max_length=20)
    Available = models.CharField(max_length=32)

class Media(models.Model):
    """
    A users supportive memories.
    An entry can be photo, text or video.
    If media type is photo then MediaExternalLink is where photo is stored.
    If media type is video then it is a youtube-url or a where video is stored.
    Memory tells if it is a memory or not.
    """

    MediaId = models.IntegerField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Compressed = models.BooleanField(default=False)
    MediaType = models.CharField(max_length=4)
    MediaTitle = models.TextField()
    MediaExternalLink = models.URLField()
    Memory = models.CharField(max_length=1)
