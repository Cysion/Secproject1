from django.db import models
from tools.crypto import gen_rsa, secret_scrambler, rsa_encrypt, rsa_decrypt, gen_aes, gen_anon_id,  rsa_encrypt_long, rsa_decrypt_long
import uuid
from login.models import User


class RelationFrom(models.Model):
    """User relation table. This table is for users to see which relationship
    the user have with other users (Friend or therapist for example).
    
    AnonymityIdFrom: Anonymity id of sharing user
    UserIdTo: User id of reciever
    Permission: Binary string where 0 denies and 1 grants permission
    UserIdFromEncrypted: User id of sharing user encrypted with recievers public key
    """
    RelationFromId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    AnonymityIdFrom = models.BinaryField(blank=False)
    UserIdTo = models.ForeignKey(User, on_delete=models.CASCADE)
    Permission = models.CharField(max_length=5)
    UserIdFromEncrypted = models.BinaryField(max_length=512)

    def getRelationFromId(self):
        return self.RelationFromId

    def getUserIdTo(self):
        return self.UserIdTo

    def getUserIdFromDecrypted(self, privKey):
        return int(rsa_decrypt(privKey.encode("utf-8"), self.UserIdFromEncrypted).decode("utf-8"))

    def getAnonymityIdFrom(self):
        return self.AnonymityIdFrom
    
    def getPermission(self):
        return self.Permission

    def setPermission(self, permission):
        self.Permission = permission

    def setUserIdFromEncrypted(self, toPubKey, userIdTo):
        self.UserIdFromEncrypted = rsa_encrypt(toPubKey,str(userIdTo).encode("utf-8"))

class RelationTo(models.Model):
    """User relation table. This table is for users to see which relationship
    the user have with other users (Friend or therapist for example).

    UserIdFrom: User id of sharing user
    AnonymityIdTo: Anonymity id of reciever
    Permission: Binary string where 0 denies and 1 grants permission
    UserIdToEncryptedTo: User id of reciever encrypted with recievers public key
    UserIdToEncryptedFrom: User id of reciever encrypted with sharing users public key
    FromPrivEncrypted: Private key of sharing user encrypted with recievers public key
    """
    RelationToId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    UserIdFrom = models.ForeignKey(User, on_delete=models.CASCADE)
    AnonymityIdTo = models.BinaryField(blank=False)
    Permission = models.CharField(max_length=5)
    UserIdToEncryptedTo = models.BinaryField(max_length=512)
    UserIdToEncryptedFrom = models.BinaryField(max_length=512)
    FromPrivEncrypted = models.BinaryField(max_length=512)

    def getRelationToId(self):
        return self.RelationToId

    def getUserIdFrom(self):
        return self.UserIdFrom

    def getUserIdToDecryptedTo(self, toPrivKey):
        return int(rsa_decrypt(toPrivKey.encode("utf-8"), self.UserIdToEncryptedTo).decode("utf-8"))

    def getUserIdToDecryptedFrom(self, fromPrivKey):
        return int(rsa_decrypt(fromPrivKey.encode("utf-8"), self.UserIdToEncryptedFrom).decode("utf-8"))

    def getPermission(self):
        return self.Permission
    
    def getAnonymityIdTo(self):
        return self.AnonymityIdTo

    def getFromPrivDecrypted(self, toPrivKey):
        return rsa_decrypt_long(toPrivKey.encode("utf-8"), self.FromPrivEncrypted)

    def setAnonymityIdTo(self, anonId):
        self.AnonymityIdTo = anonId

    def setFromPrivEncrypted(self, toPub, fromPriv):
        self.FromPrivEncrypted = rsa_encrypt_long(toPub, fromPriv.encode("utf-8"))

    def setPermission(self, permission):
        self.Permission = permission

    def setUserIdToEncryptedFrom(self, fromPubKey, userIdTo):
        self.UserIdToEncryptedFrom = rsa_encrypt(fromPubKey, str(userIdTo).encode("utf-8"))
    
    def setUserIdToEncryptedTo(self, toPubKey, userIdTo):
        self.UserIdToEncryptedTo = rsa_encrypt(toPubKey, str(userIdTo).encode("utf-8"))