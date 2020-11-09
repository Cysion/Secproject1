from django.db import models
from tools.crypto import gen_rsa, secret_scrambler, rsa_encrypt, rsa_decrypt


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
    Pubkey = models.CharField(
        max_length=500,
        blank=False,
    )

    Role_Choices = [
        ('User', 'User'),
        ('Caretaker', 'Caretaker'),
        ('Admin', 'Admin')
    ]

    Role = models.CharField(
        max_length=9,
        choices=Role_Choices
    )
    Symkey = models.CharField(max_length=256)

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
        return rsa_decrypt(privKey.encode("utf-8"), self.DateOfBirth).decode("utf-8")
    
    def getEmail(self):
        return self.Email

    def setPubKey(self, pubKey):
        self.Pubkey=pubKey
        return 0

    def setGender(self, gender):
        if self.Pubkey:
            self.Gender=rsa_encrypt(self.Pubkey.encode("utf-8"), gender.encode("utf-8"))
            return 0
        else:
            return 1

    def setFirstName(self, firstName):
        if self.Pubkey:
            self.FirstName=rsa_encrypt(self.Pubkey.encode("utf-8"), firstName.encode("utf-8"))
            return 0
        else:
            return 1

    def setLastName(self, lastName):
        if self.Pubkey:
            self.LastName=rsa_encrypt(self.Pubkey.encode("utf-8"), lastName.encode("utf-8"))
            return 0
        else:
            return 1

    def setDateOfBirth(self, dateOfBirth):
        if self.Pubkey:
            self.DateOfBirth=rsa_encrypt(self.Pubkey.encode("utf-8"), dateOfBirth.encode("utf-8)"))
            return 0
        else:
            return 1

    def setEmail(self, email):
        self.Email = email
        return 0
    
    def createSymkey(self):
        pass

    

class RelationFrom(models.Model):
    """User relation table. This table is for users to see which relationship
    the user have with other users (Friend or therapist for example).

    UserIdTo: Friend, Family or therapist user id.
    AnonymityIdFrom: The current user. To see which this user have
    relationsships to.
    Permission: a bit string where 0 says no permission and 1 says
    got permission for each permission entry.
    Key: The public key of the UserIdTo.
    """
    RelationFromId = models.IntegerField(primary_key=True)
    AnonymityIdFrom = models.IntegerField(blank=False)
    UserIdTo = models.ForeignKey(User, on_delete=models.CASCADE)
    Permission = models.CharField(max_length=4)
    Key = models.CharField(max_length=64)

class RelationTo(models.Model):
    """User relation table. This table is for users to see which relationship
    the user have with other users (Friend or therapist for example).

    UserIdTo: Friend, Family or therapist user id.
    AnonymityIdFrom: The current user. To see which this user have
    relationsships to.
    Permission: a bit string where 0 says no permission and 1 says
    got permission for each permission entry.
    Key: The public key of the AnonymityIdTo.
    """
    RelationToId = models.IntegerField(primary_key=True)
    UserIdFrom = models.ForeignKey(User, on_delete=models.CASCADE)
    AnonymityIdTo = models.IntegerField(blank=False)
    Permission = models.CharField(max_length=4)
    Key = models.CharField(max_length=64)


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
