from django.db import models
from tools.crypto import gen_rsa, secret_scrambler, rsa_encrypt, rsa_decrypt, gen_aes, gen_anon_id,  rsa_encrypt_long, rsa_decrypt_long
import uuid
from login.models import User


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

    def setPermission(self, permission):
        self.Permission = permission

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
    RelationToId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    UserIdFrom = models.ForeignKey(User, on_delete=models.CASCADE)
    AnonymityIdTo = models.BinaryField(blank=False)
    Permission = models.CharField(max_length=5)
    UserIdToEncrypted = models.BinaryField(max_length=512)
    FromPrivEncrypted = models.BinaryField(max_length=512)

    def getUserIdFrom(self):
        return self.UserIdFrom

    def getUserIdToDecrypted(self, toPrivKey):
        return int(rsa_decrypt(toPrivKey.encode("utf-8"), self.UserIdToEncrypted).decode("utf-8"))

    def getPermission(self):
        return self.Permission
    
    def getAnonymityIdTo(self):
        return self.AnonymityIdTo

    def getFromPrivDecrypted(self, toPrivKey):
        return rsa_decrypt_long(toPrivKey.encode("utf-8"), self.FromPrivEncrypted)

    def setAnonymityIdTo(self, anonId):
        self.AnonymityIdTo = anonId

    def setFromPrivEncrypted(self, toPub, fromPriv):
        self.rsa_encrypt(toPub, fromPriv.encode("utf-8"))

    def setPermission(self, permission):
        self.Permission = permission
