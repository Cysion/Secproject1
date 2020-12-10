from django.db import models
from tools.crypto import rsa_encrypt, rsa_decrypt, rsa_encrypt_long, rsa_decrypt_long, aes_encrypt, aes_decrypt

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
    MediaType = models.BinaryField(max_length=512)
    MediaTitle = models.BinaryField(max_length=512)
    MediaText = models.BinaryField(max_length=768)
    MediaLink = models.BinaryField(max_length=512)
    Memory = models.BinaryField(max_length=512)
    MediaSize = models.BinaryField(max_length=512)


    def getMediaId(self):
        return self.MediaId


    def getUserId(self):
        return self.UserId

    def getMediaType(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.MediaType).decode("utf-8")

    def getMediaTitle(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.MediaTitle).decode("utf-8")

    def getMediaText(self, privKey):
        return rsa_decrypt_long(privKey.encode("utf-8"), self.MediaText).decode("utf-8")

    def getLink(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.MediaLink).decode("utf-8")

    def getMemory(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.Memory).decode("utf-8")

    def getMediaSize(self, privKey):
        return rsa_decrypt(privKey.encode("utf-8"), self.MediaSize).decode("utf-8")


    def setMediaType(self, PubKey, mediaType):
            self.MediaType=rsa_encrypt(PubKey, mediaType.encode("utf-8)"))


    def setMediaTitle(self, PubKey, title):
            self.MediaTitle=rsa_encrypt(PubKey, title.encode("utf-8)"))


    def setMediaText(self, PubKey, text):
            self.MediaText=rsa_encrypt_long(PubKey, text.encode("utf-8)"))


    def setLink(self, PubKey, link):
            self.MediaLink=rsa_encrypt(PubKey, link.encode("utf-8)"))


    def setMemory(self, PubKey, memory):
            self.Memory=rsa_encrypt(PubKey, memory.encode("utf-8)"))


    def setMediaSize(self, PubKey, size):
            self.MediaSize=rsa_encrypt(PubKey, str(size).encode("utf-8"))


class Diary(models.Model):
    DiaryId = models.AutoField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Date = models.BinaryField(max_length=512)
    Text = models.BinaryField(max_length=768)
    Timestamp = models.BinaryField(max_length=512)

    def getDiaryId(self):
        return self.DiaryId
    
    def getUserId(self):
        return self.UserId

    def getDate(self, symKey):
        return aes_decrypt(symKey, self.Date).decode("utf-8")

    def getText(self, symKey):
        return aes_decrypt(symKey, self.Text).decode("utf-8")

    def getTimestamp(self, symKey):
        return aes_decrypt(symKey, self.Timestamp).decode("utf-8")

    def setUserId(self, user):
        self.UserId = user

    def setDate(self, symKey, date):
        self.Date = aes_encrypt(symKey, date.encode("utf-8"))

    def setText(self, symKey, text):
        self.Text = aes_encrypt(symKey, text.encode("utf-8"))

    def setTimestamp(self, symKey, timestamp):
        self.Timestamp = aes_encrypt(symKey, timestamp.encode("utf-8"))

    def lessThan(self, other, symKey):
        selfDate = self.getDate(symKey)
        otherDate = other.getDate(symKey)
        if selfDate != otherDate:
            return selfDate < otherDate
        return self.getTimestamp(symKey) < other.getTimestamp(symKey)
    