from django.db import models
from login.models import User
# Create your models here.

class Check(models.Model):
    """
    A rating a day.
    Rating can be
        g = Green, health+ activities
        o = Orange, no health+/- activities
        r = Red, unhealthy activities.
    """

    CheckId = models.IntegerField(primary_key=True)
    UserId = models.ForeignKey(User, on_delete=models.CASCADE)
    Date = models.DateField(auto_now=True)
    Rating = models.CharField(max_length=1)
