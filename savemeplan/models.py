from django.db import models
from login.models import User
from tools.crypto import rsa_encrypt, rsa_decrypt, rsa_encrypt_long, rsa_decrypt_long, aes_encrypt, aes_decrypt

# Create your models here.

class SaveMePlan(models.Model):
    """
    Save.Me plan data.

    Step: the plan step.
    Value: Rating between either 0-9 or 0-4 deppending on step.
    Time: Used be researcher
    """

    SaveMePlanId = models.IntegerField()
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Step = models.BinaryField(max_length=512)
    Text = models.BinaryField(max_length=512)
    Value = models.BinaryField(max_length=512)
    Time = models.BinaryField(max_length=512)

    def setStep(self, symkey, step):
        self.Step = aes_encrypt(symkey, step.encode("utf-8"))

    def setText(self, symkey, text):
        self.Text = aes_encrypt(symkey, text.encode("utf-8"))

    def setValue(self, symkey, value):
        self.Value = aes_encrypt(symkey, value.encode("utf-8"))

    def setTime(self, symkey, time):
        self.Time = aes_encrypt(symkey, time.encode("utf-8"))

    def getId(self):
        return self.SaveMePlanId

    def getStep(self, symkey):
        return aes_decrypt(symkey, self.Step).decode("utf8")

    def getText(self, symkey):
        return aes_decrypt(symkey, self.Text).decode("utf8")

    def getValue(self, symkey):
        return aes_decrypt(symkey, self.Value).decode("utf8")

    def getTime(self, symkey):
        return aes_decrypt(symkey, self.Time).decode("utf8")

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
