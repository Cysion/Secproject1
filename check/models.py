from django.db import models
from login.models import User
# Create your models here.

from tools.crypto import aes_encrypt, aes_decrypt

class Check(models.Model):
    """
    A rating a day.
    Rating can be
        g = Green, health+ activities
        o = Orange, no health+/- activities
        r = Red, unhealthy activities.
    """

    CheckId = models.AutoField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Date = models.DateField()
    Rating = models.BinaryField(max_length=512)

    def setDate(self, date):
        print(date)
        self.Date = date

    def setRating(self, symkey, rating):
        self.Rating = aes_encrypt(symkey, rating.encode('utf-8'))

    def getDate(self):
        return self.Date

    def getRating(self, symkey):
        return aes_decrypt(symkey, self.Rating).decode('utf-8')
