from django.db import models
from login.models import User
from tools.crypto import rsa_encrypt, rsa_decrypt, rsa_encrypt_long, rsa_decrypt_long

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

    def setName(self, name):
        self.Name = rsa_encrypt(UserId.getPubkey(), name.encode("utf-8"))
    
    def setPhoneNumber(self, phoneNumber):
        self.Phonenumber = rsa_encrypt(UserId.getPubkey(), phoneNumber.encode("utf-8"))

    def setAvailable(self, available):
        self.available = rsa_encrypt(UserId.getPubkey(), available.encode("utf-8"))

    def getName(self,privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Name).decode("utf8")

    def getPhonenumber(self,privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.PhoneNumber).decode("utf8")

    def getAvailable(self,privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Available).decode("utf8")

    
