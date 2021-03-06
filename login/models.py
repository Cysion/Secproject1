from django.db import models
from tools.crypto import gen_rsa, secret_scrambler, rsa_encrypt, rsa_decrypt, gen_aes, gen_anon_id, rsa_encrypt_long, rsa_decrypt_long


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
    Symkey = models.BinaryField(max_length=512)
    AnonId = models.BinaryField(max_length=512)
    CreationDate = models.BinaryField(max_length=512)

    def getUid(self):
        return self.UserId

    def getGender(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Gender).decode("utf-8")

    def getFirstName(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.FirstName).decode("utf-8")

    def getLastName(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.LastName).decode("utf-8")
    
    def getName(self, privKey):
            return f"{self.getFirstName(privKey)} {self.getLastName(privKey)}"

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

    def getCreationDate(self, privKey):
        return rsa_decrypt_long(privKey, self.CreationDate).decode('utf-8')

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

    def setSymkey(self, Symkey=None):
        if self.Pubkey:
            if not Symkey:
                Symkey=gen_aes()
            self.Symkey=rsa_encrypt(self.Pubkey,Symkey)
            return 0
        else:
            return 1

    def setRole(self, role):
        self.Role=role

    def setAnonId(self, privKey):
        self.AnonId=rsa_encrypt_long(self.Pubkey, gen_anon_id(self.UserId, self.getDateOfBirth(privKey)))

    def setCreationDate(self, creation):
        self.CreationDate = rsa_encrypt(self.Pubkey, str(creation).encode('utf-8'))