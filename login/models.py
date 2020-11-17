from django.db import models
from tools.crypto import gen_rsa, secret_scrambler, rsa_encrypt, rsa_decrypt, gen_aes, gen_anon_id, rsa_encrypt_long, rsa_decrypt_long



# Create your models here.

class User(models.Model):
    '''
    This is the User model which will have information about the user.
    '''
    UserId = models.AutoField(primary_key=True)
    Gender = models.BinaryField(max_length=512)
    FirstName = models.BinaryField(max_length=512, blank=False)
    LastName = models.BinaryField(max_length=512, blank=False)
    DateOfBirth = models.BinaryField(max_length=512, blank=False)
    Email = models.CharField(
        max_length=128,
        blank=False,
        unique=True
    )
    Pubkey = models.BinaryField(
        max_length=512,
        blank=False,
    )

    Role_Choices = [
        ('User', 'User'),
        ('Professional', 'Professional'),
        ('Admin', 'Admin')
    ]

    Role = models.CharField(
        max_length=12,
        choices=Role_Choices
    )
    Symkey = models.BinaryField(max_length=256)
    AnonId = models.BinaryField(max_length=512)

    def getUid(self):
        return self.UserId

    def getGender(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Gender).decode("utf-8")

    def getFirstName(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.FirstName).decode("utf-8")

    def getLastName(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.LastName).decode("utf-8")

    def getDateOfBirth(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.DateOfBirth).decode("utf-8")

    def getSymKey(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Symkey)

    def getEmail(self):
        return self.Email.lower()

    def getPubkey(self):
        return self.Pubkey

    def getRole(self):
        return self.Role

    def getAnonId(self, privKey):
        return rsa_decrypt_long(privKey, self.AnonId)


    def setPubKey(self, pubKey):
        self.Pubkey=pubKey
        return 0

    def setGender(self, gender):
        if self.Pubkey:
            self.Gender=rsa_encrypt(self.Pubkey, gender.encode("utf-8"))
            return 0
        else:
            return 1

    def setFirstName(self, firstName):
        if self.Pubkey:
            self.FirstName=rsa_encrypt(self.Pubkey, firstName.capitalize().encode("utf-8"))
            return 0
        else:
            return 1

    def setLastName(self, lastName):
        if self.Pubkey:
            self.LastName=rsa_encrypt(self.Pubkey, lastName.capitalize().encode("utf-8"))
            return 0
        else:
            return 1

    def setDateOfBirth(self, dateOfBirth):
        if self.Pubkey:
            self.DateOfBirth=rsa_encrypt(self.Pubkey, dateOfBirth.encode("utf-8)"))
            return 0
        else:
            return 1

    def setEmail(self, email):
        self.Email = email
        return 0

    def setSymkey(self):
        if self.Pubkey:
            self.Symkey=rsa_encrypt(self.Pubkey, gen_aes())
            return 0
        else:
            return 1

    def setRole(self, role):
        self.Role=role

    def setAnonId(self, privKey):
        self.AnonId=rsa_encrypt_long(self.Pubkey, gen_anon_id(self.UserId, self.getDateOfBirth(privKey)))

    

class Action(models.Model):
    """
    Is connected to ResearchData.
    The description will contain a descritive message about what a user has
    done.
    """

    ActionId = models.IntegerField(primary_key=True)
    Description = models.CharField(max_length=255)

class ResearchData(models.Model):
    """
    Data researchers should have.
    AnonymityCode = is a code which is generated from data from a users and
    cannot be reversed.
    """

    ResearchDataId = models.IntegerField(primary_key=True)
    ActionId = models.ForeignKey(Action, on_delete=models.CASCADE)
    AnonymityCode = models.CharField(max_length=64)
    Time = models.DateTimeField(auto_now=True)
