from django.db import models
from tools.crypto import rsa_encrypt, rsa_decrypt

# Create your models here.

from login.models import User

class Media(models.Model):
    """
    A users supportive memories.
    An entry can be photo, text or video.
    If media type is photo then MediaLink is where photo is stored.
    If media type is video then it is a youtube-url or a where video is stored.
    Memory tells if it is a memory or not.
    """

    MediaId = models.AutoField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Compressed = models.BinaryField(max_length=1)
    MediaType = models.BinaryField(max_length=4)
    MediaTitle = models.BinaryField(max_length=64)
    MediaText = models.BinaryField()
    MediaLink = models.BinaryField()
    Memory = models.CharField(max_length=1)
    MediaSize = models.BinaryField(max_length=12)

    def getCompressed(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Compressed).decode("utf-8")

    def getMediaType(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.MediaType).decode("utf-8")

    def getMediaTitle(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.MediaTitle).decode("utf-8")

    def getMediaText(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.MediaText).decode("utf-8")

    def getLink(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.MediaLink).decode("utf-8")

    def getMemory(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Memory).decode("utf-8")

    def getMediaSize(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.MediaSize).decode("utf-8")

    def setCompressed(self, PubKey, compressed):
        if PubKey:
            self.Compressed=rsa_encrypt(Pubkey, compressed.encode("utf-8)"))
            return 0
        else:
            return 1

    def setMediaType(self, PubKey, type):
        if PubKey:
            self.MediaType=rsa_encrypt(PubKey, type.encode("utf-8)"))
            return 0
        else:
            return 1

    def setMediaTitle(self, PubKey, title):
        if PubKey:
            self.MediaTitle=rsa_encrypt(PubKey, title.encode("utf-8)"))
            return 0
        else:
            return 1

    def setMediaText(self, PubKey, text):
        if PubKey:
            self.MediaText=rsa_encrypt(PubKey, text.encode("utf-8)"))
            return 0
        else:
            return 1

    def setLink(self, PubKey, link):
        if PubKey:
            self.MediaLink=rsa_encrypt(PubKey, link.encode("utf-8)"))
            return 0
        else:
            return 1

    def setMemory(self, PubKey, memory):
        if PubKey:
            self.Memory=rsa_encrypt(PubKey, memory.encode("utf-8)"))
            return 0
        else:
            return 1

    def setMediaSize(self, PubKey, size):
        if PubKey:
            self.MediaSize=rsa_encrypt(PubKey, str(size).encode("utf-8"))
            return 0
        else:
            return 1
