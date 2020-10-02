from django.db import models
from login.models import User

# Create your models here.

class SaveMePlan(models.Model):
    SaveMePlanId = models.IntegerField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Step = models.CharField(max_length=2, blank=False)
    Text = models.CharField(max_length=120)
    Value = models.IntegerField(blank=False)
    Time = models.DateTimeField(auto_now=True)

class Contacts(models.Model):
    ContactsId = models.IntegerField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Name = models.CharField(max_length=120)
    Phonenumber = models.CharField(max_length=20)
    Available = models.CharField(max_length=32)

class Media(models.Model):
    MediaId = models.IntegerField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Compressed = models.BooleanField(default=False)
    MediaType = models.CharField(max_length=4)
    MediaTitle = models.TextField()
    MediaExternalLink = models.URLField()
    Memory = models.CharField(max_length=1)
