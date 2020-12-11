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

    SaveMePlanId = models.AutoField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Step = models.BinaryField(max_length=512)
    Text = models.BinaryField(max_length=512)
    Value = models.BinaryField(max_length=512)
    Time = models.BinaryField(max_length=512)

    def setStep(self, step):
        self.Step = rsa_encrypt(self.UserId.getPubkey(), step.encode("utf-8"))

    def setText(self, text):
        self.Text = rsa_encrypt(self.UserId.getPubkey(), text.encode("utf-8"))

    def setValue(self, value):
        self.Value = rsa_encrypt(self.UserId.getPubkey(), value.encode("utf-8"))

    def setTime(self, time):
        self.Time = rsa_encrypt(self.UserId.getPubkey(), time.encode("utf-8"))

    def getStep(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Step).decode("utf8")

    def getText(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Text).decode("utf8")

    def getValue(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Value).decode("utf8")

    def getTime(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Time).decode("utf8")

class Contacts(models.Model):
    """
    Available contacts for the user.
    Storing information such as Contact name, their phone number and
    when they are available.
    """

    ContactsId = models.AutoField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Name = models.BinaryField(max_length=512)
    Phonenumber = models.BinaryField(max_length=512)
    Available = models.BinaryField(max_length=512)

    def setName(self, name):
        self.Name = rsa_encrypt(self.UserId.getPubkey(), name.encode("utf-8"))

    def setPhonenumber(self, phoneNumber):
        self.Phonenumber = rsa_encrypt(self.UserId.getPubkey(), phoneNumber.encode("utf-8"))

    def setAvailable(self, available):
        self.Available = rsa_encrypt(self.UserId.getPubkey(), available.encode("utf-8"))

    def getName(self,privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Name).decode("utf8")

    def getPhonenumber(self,privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Phonenumber).decode("utf8")

    def getAvailable(self,privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Available).decode("utf8")
